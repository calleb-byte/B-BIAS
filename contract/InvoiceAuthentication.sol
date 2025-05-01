// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract InvoiceAuthentication {
    address public admin;

    struct Invoice {
        bytes32 invoiceHash;
        address submittedBy;
        uint256 timestamp;
        bool isValid;
    }

    mapping(bytes32 => Invoice) public invoices;

    event InvoiceSubmitted(bytes32 indexed invoiceHash, address indexed submittedBy, uint256 timestamp);
    event InvoiceInvalidated(bytes32 indexed invoiceHash);

    constructor() {
        admin = msg.sender;
    }

    function submitInvoice(bytes32 _invoiceHash) public {
        require(invoices[_invoiceHash].timestamp == 0, "Invoice already exists");

        invoices[_invoiceHash] = Invoice({
            invoiceHash: _invoiceHash,
            submittedBy: msg.sender,
            timestamp: block.timestamp,
            isValid: true
        });

        emit InvoiceSubmitted(_invoiceHash, msg.sender, block.timestamp);
    }

    function verifyInvoice(bytes32 _invoiceHash) public view returns (bool, address, uint256) {
        Invoice memory inv = invoices[_invoiceHash];
        require(inv.timestamp != 0, "Invoice not found");
        return (inv.isValid, inv.submittedBy, inv.timestamp);
    }

    function invalidateInvoice(bytes32 _invoiceHash) public {
        require(msg.sender == admin, "Only admin can invalidate");
        require(invoices[_invoiceHash].isValid, "Invoice already invalid");

        invoices[_invoiceHash].isValid = false;
        emit InvoiceInvalidated(_invoiceHash);
    }
}
