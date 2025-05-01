# Blockchain-Based Invoice Authentication System

A full-stack blockchain-based solution for secure invoice verification, fraud prevention, and real-time stakeholder notifications using Solidity, MySQL, Africa's Talking, and raw Python backend.

## Tech Stack
- Solidity (Smart Contracts)
- MySQL (Invoice/User Storage)
- Python (Backend, no frameworks)
- HTML/CSS/JS (Frontend)
- Africa's Talking (SMS notifications)

## Project Structure
```
.
├── backend.py
├── config.py
├── contract/
│   └── InvoiceAuthentication.sol
├── db/
│   └── schema.sql
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── style.css
│   └── script.js
```

## Setup Instructions

1. Install Python packages
pip install web3 mysql-connector-python 

2. Deploy Smart Contract
Use Remix or Truffle + Ganache. Copy contract address and ABI into config.py

3. Configure Backend
Edit config.py with your blockchain, database, and Africa's credentials

4. Run MySQL Script
Source db/schema.sql;

5. Start Backend
python backend.py

6. Open Frontend
Open index.html in browser
