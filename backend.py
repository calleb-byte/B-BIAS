from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import json
import re
from web3 import Web3
import mysql.connector
import africastalking
from eth_utils import keccak
from config import (
    contract_address, contract_abi, ganache_url, mysql_config,
    admin_private_key, admin_address, africastalking_username, africastalking_api_key
)

w3 = Web3(Web3.HTTPProvider(ganache_url))
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

conn = mysql.connector.connect(**mysql_config)
cursor = conn.cursor(buffered=True)

africastalking.initialize(africastalking_username, africastalking_api_key)
sms_client = africastalking.SMS

def send_sms(to, message):
    try:
        response = sms_client.send(message, [to])
        print("SMS Response:", response)
    except Exception as e:
        print(f"SMS sending error: {e}")

class RequestHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(length)
        data = json.loads(post_data)

        if self.path == '/submit-invoice':
            self.submit_invoice(data)
        elif self.path == '/verify-invoice':
            self.verify_invoice(data)
        elif self.path == '/register':
            self.register_user(data)
        elif self.path == '/login':
            self.login_user(data)
        elif self.path == '/mark-paid':
            self.mark_paid(data)
        else:
            self.respond({'error': 'Invalid endpoint'}, 404)

    def submit_invoice(self, data):
        try:
            invoice_data = data['invoice']
            user = data['user']
            phone = data['phone']
        except KeyError as e:
            self.respond({'error': f"Missing required field: {str(e)}"}, 400)
            return

        required_fields = ["INVOICE", "Invoice Number:", "Invoice Date:", "Bill To:", "Items:", "Total Amount:"]
        if not all(field in invoice_data for field in required_fields):
            self.respond({'error': 'Invalid invoice structure. Missing fields.'}, 400)
            return

        invoice_data = invoice_data.strip().replace("\n", " ").replace("\r", "")

        match = re.search(r"Invoice Number:\s*([A-Za-z0-9\-]+)", invoice_data)
        if not match:
            self.respond({'error': 'Invoice Number not found in invoice data.'}, 400)
            return
        invoice_number = match.group(1)

        cursor.execute("SELECT id FROM invoices WHERE invoice_number=%s", (invoice_number,))
        if cursor.fetchone():
            message = f"Duplicate invoice number '{invoice_number}' detected. Already submitted."
            send_sms(phone, f"Hi {user}, your invoice submission failed: {message}")
            self.respond({'error': message}, 400)
            return

        invoice_hash = keccak(invoice_data.encode())

        cursor.execute("SELECT id FROM invoices WHERE hash=%s", (invoice_hash.hex(),))
        if cursor.fetchone():
            message = "Duplicate invoice detected based on content hash."
            send_sms(phone, f"Hi {user}, your invoice submission failed: {message}")
            self.respond({'error': message}, 400)
            return

        try:
            is_valid, _, _ = contract.functions.verifyInvoice(invoice_hash).call()
            if is_valid:
                message = "This invoice already exists on the blockchain."
                send_sms(phone, f"Hi {user}, submission failed: {message}")
                self.respond({'error': message}, 400)
                return
        except Exception as e:
            print(f"Blockchain check failed: {e}")

        nonce = w3.eth.get_transaction_count(admin_address)
        txn = contract.functions.submitInvoice(invoice_hash).build_transaction({
            'chainId': 1337,
            'gas': 300000,
            'gasPrice': w3.to_wei('1', 'gwei'),
            'nonce': nonce
        })

        try:
            signed_txn = w3.eth.account.sign_transaction(txn, private_key=admin_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        except Exception as blockchain_error:
            self.respond({'error': f"Blockchain error: {str(blockchain_error)}"}, 500)
            return

        try:
            cursor.execute(
                "INSERT INTO invoices (user, hash, status, tx_hash, invoice_number) VALUES (%s, %s, %s, %s, %s)",
                (user, invoice_hash.hex(), 'valid', tx_hash.hex(), invoice_number)
            )
            conn.commit()
            send_sms(phone, f"Hi {user}, your invoice was submitted successfully. TxHash: {tx_hash.hex()}")
            self.respond({'message': 'Invoice submitted successfully.', 'tx': tx_hash.hex()})
        except Exception as e:
            print(f"MySQL insert error: {e}")
            self.respond({'error': 'Failed to save invoice in DB.'}, 500)

    def verify_invoice(self, data):
        try:
            invoice_data = data['invoice']
            invoice_hash = keccak(invoice_data.encode())
            is_valid, submitted_by, timestamp = contract.functions.verifyInvoice(invoice_hash).call()
            self.respond({
                'status': 'valid' if is_valid else 'invalid',
                'submitter': submitted_by,
                'timestamp': timestamp
            })
        except Exception as e:
            print(f"Verify invoice error: {e}")
            self.respond({'status': 'not found'})

    def mark_paid(self, data):
        try:
            invoice_data = data['invoice']
            invoice_hash = keccak(invoice_data.encode())
            phone = data['phone']
            user = data['user']

            cursor.execute("UPDATE invoices SET status='paid' WHERE hash=%s", (invoice_hash.hex(),))
            conn.commit()

            send_sms(phone, f"Hi {user}, your invoice has been marked as PAID.")
            self.respond({'message': 'Invoice marked as paid.'})
        except Exception as e:
            print(f"Mark paid error: {e}")
            self.respond({'error': str(e)}, 500)

    def register_user(self, data):
        try:
            username = data['username']
            password = hashlib.sha256(data['password'].encode()).hexdigest()
            phone = data['phone']

            cursor.execute("SELECT id FROM users WHERE username=%s OR phone=%s", (username, phone))
            if cursor.fetchone():
                self.respond({'message': 'Username or phone already exists.'})
                return

            cursor.execute("INSERT INTO users (username, password, phone) VALUES (%s, %s, %s)",
                           (username, password, phone))
            conn.commit()
            self.respond({'message': 'User registered successfully.'})
        except Exception as e:
            print(f"Register error: {e}")
            self.respond({'error': str(e)}, 500)

    def login_user(self, data):
        try:
            username = data['username']
            password = hashlib.sha256(data['password'].encode()).hexdigest()

            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()

            self.respond({'message': 'Login success' if user else 'Login failed'})
        except Exception as e:
            print(f"Login error: {e}")
            self.respond({'error': str(e)}, 500)

    def respond(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run():
    server = HTTPServer(('localhost', 8080), RequestHandler)
    print("Server running at http://localhost:8080")
    server.serve_forever()

if __name__ == "__main__":
    run()
