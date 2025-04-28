from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import hashlib
from web3 import Web3
import mysql.connector
from twilio.rest import Client
from config import contract_address, contract_abi, ganache_url, mysql_config, admin_private_key, admin_address, twilio_sid, twilio_token, twilio_number

# Connect to blockchain
w3 = Web3(Web3.HTTPProvider(ganache_url))
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Connect to MySQL
conn = mysql.connector.connect(**mysql_config)
cursor = conn.cursor(buffered=True)  # ✅ Buffered to avoid unread results

# Setup Twilio
sms_client = Client(twilio_sid, twilio_token)

def send_sms(to, message):
    try:
        sms_client.messages.create(body=message, from_=twilio_number, to=to)
    except Exception as e:
        print(f"SMS sending error: {e}")

class RequestHandler(BaseHTTPRequestHandler):

    # Handle CORS preflight
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # Handle POST routes
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

            # Validate invoice structure
            required_fields = ["INVOICE", "Invoice Number:", "Invoice Date:", "Bill To:", "Items:", "Total Amount:"]
            if not all(field in invoice_data for field in required_fields):
                self.respond({'error': 'Invalid invoice structure. Please ensure all required fields are present.'}, 400)
                return

            invoice_hash = hashlib.sha256(invoice_data.encode()).hexdigest()
            hash_bytes = bytes.fromhex(invoice_hash)

            nonce = w3.eth.get_transaction_count(admin_address)
            txn = contract.functions.submitInvoice(hash_bytes).build_transaction({
                'chainId': 1337,
                'gas': 300000,
                'gasPrice': w3.to_wei('1', 'gwei'),
                'nonce': nonce
            })
            signed_txn = w3.eth.account.sign_transaction(txn, private_key=admin_private_key)

            try:
                tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            except Exception as blockchain_error:
                error_message = str(blockchain_error)
                if "Invoice already exists" in error_message:
                    self.respond({'error': 'Invoice already exists. Please submit a new invoice.'}, 400)
                else:
                    self.respond({'error': 'Blockchain error during invoice submission.'}, 500)
                return

            # Save in database if blockchain success
            cursor.execute("INSERT INTO invoices (user, hash, status, tx_hash) VALUES (%s, %s, %s, %s)",
                           (user, invoice_hash, 'valid', tx_hash.hex()))
            conn.commit()

            send_sms(phone, f"Hi {user}, your invoice has been successfully submitted. TxHash: {tx_hash.hex()}")
            self.respond({'message': 'Invoice submitted and SMS sent', 'tx': tx_hash.hex()})

        except Exception as e:
            print(f"Submit invoice general error: {e}")
            self.respond({'error': str(e)}, 500)

    def verify_invoice(self, data):
        try:
            invoice_data = data['invoice']
            invoice_hash = hashlib.sha256(invoice_data.encode()).hexdigest()
            hash_bytes = bytes.fromhex(invoice_hash)

            is_valid, submitted_by, timestamp = contract.functions.verifyInvoice(hash_bytes).call()
            self.respond({'status': 'valid' if is_valid else 'invalid', 'submitter': submitted_by, 'timestamp': timestamp})
        except Exception as e:
            print(f"Verify invoice error: {e}")
            self.respond({'status': 'not found'})

    def mark_paid(self, data):
        try:
            invoice_data = data['invoice']
            invoice_hash = hashlib.sha256(invoice_data.encode()).hexdigest()
            phone = data['phone']
            user = data['user']

            cursor.execute("UPDATE invoices SET status='paid' WHERE hash=%s", (invoice_hash,))
            conn.commit()

            send_sms(phone, f"Hi {user}, your invoice has been marked as PAID. Thank you!")
            self.respond({'message': 'Invoice marked as paid and SMS sent'})
        except Exception as e:
            print(f"Mark paid error: {e}")
            self.respond({'error': str(e)}, 500)

    def register_user(self, data):
        try:
            username = data['username']
            password = hashlib.sha256(data['password'].encode()).hexdigest()
            phone = data['phone']

            cursor.execute("SELECT id FROM users WHERE username=%s OR phone=%s", (username, phone))
            existing_user = cursor.fetchone()

            if existing_user:
                self.respond({'message': 'Username or phone already registered.'})
                return

            cursor.execute("INSERT INTO users (username, password, phone) VALUES (%s, %s, %s)", (username, password, phone))
            conn.commit()
            self.respond({'message': 'User registered successfully'})
        except Exception as e:
            print(f"Registration error: {e}")
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

# Server runner
def run():
    server = HTTPServer(('localhost', 8080), RequestHandler)
    print("Server running on http://localhost:8080")
    server.serve_forever()

if __name__ == "__main__":
    run()
