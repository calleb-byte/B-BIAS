ganache_url = "http://127.0.0.1:7545"
contract_address = "0xf8d67CAb41fe00e482513Ce81E298e6e1e244c13"

contract_abi = [
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "_invoiceHash",
                "type": "bytes32"
            }
        ],
        "name": "invalidateInvoice",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "invoiceHash",
                "type": "bytes32"
            }
        ],
        "name": "InvoiceInvalidated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "bytes32",
                "name": "invoiceHash",
                "type": "bytes32"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "submittedBy",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "name": "InvoiceSubmitted",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "_invoiceHash",
                "type": "bytes32"
            }
        ],
        "name": "submitInvoice",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "admin",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "name": "invoices",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "invoiceHash",
                "type": "bytes32"
            },
            {
                "internalType": "address",
                "name": "submittedBy",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "isValid",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "_invoiceHash",
                "type": "bytes32"
            }
        ],
        "name": "verifyInvoice",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            },
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

admin_address = "0x9815960628158E79C4C30752765a380b61Af3D20"
admin_private_key = "0x9623337ebc936650bf245527a32210b98d66c34c1f32eca34232a3124d6cdd4e"

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'riga',
    'database': 'invoice_auth'
}

# ✅ Replaced Twilio credentials with Africa's Talking
africastalking_username = "sandbox"
africastalking_api_key = "atsk_aafc30ad4203633117e674ea2773077feefe774aa5679d70dbae95ad1fba18b5bc3ebde3"
africastalking_sender = "AFRICASTKG"  # Optional: registered sender ID

