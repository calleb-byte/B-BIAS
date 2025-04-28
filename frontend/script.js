const API_URL = "http://localhost:8080";

// ✅ Phone format validation
function isValidPhone(phone) {
  const pattern = /^\+254[0-9]{9}$/;
  return pattern.test(phone);
}

// ✅ Invoice basic structure validation
function isValidInvoice(invoice) {
  return invoice.includes("INVOICE") &&
         invoice.includes("Invoice Number:") &&
         invoice.includes("Invoice Date:") &&
         invoice.includes("Bill To:") &&
         invoice.includes("Items:") &&
         invoice.includes("Total Amount:");
}

// ✅ Login Function
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || password.length < 4) {
    alert("Username required. Password must be at least 4 characters.");
    return;
  }

  try {
    const res = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const result = await res.json();
    document.getElementById("auth-message").innerText = result.message || "Login failed. Please try again.";

    if (result.message && result.message.toLowerCase().includes("success")) {
      window.location.href = "dashboard.html";
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("Failed to connect to server during login.");
  }
}

// ✅ Register Function (with duplicate prevention message)
async function register() {
  const username = document.getElementById("reg-username").value.trim();
  const password = document.getElementById("reg-password").value.trim();
  const confirmPassword = document.getElementById("reg-confirm-password").value.trim();
  const phone = document.getElementById("reg-phone").value.trim();

  if (!username || password.length < 4) {
    alert("Username required. Password must be at least 4 characters.");
    return;
  }
  if (password !== confirmPassword) {
    alert("Passwords do not match!");
    return;
  }
  if (!isValidPhone(phone)) {
    alert("Invalid phone format. Use +2547XXXXXXXX");
    return;
  }

  try {
    const res = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, phone })
    });
    const result = await res.json();

    if (result.message && result.message.toLowerCase().includes("registered successfully")) {
      alert("Registration successful! You can now log in.");
      document.getElementById("auth-message").innerText = "";
    } else if (result.message && result.message.toLowerCase().includes("already registered")) {
      alert("Username or phone number already registered.");
      document.getElementById("auth-message").innerText = "Username or phone already exists.";
    } else {
      alert("Registration failed. Please try again.");
      document.getElementById("auth-message").innerText = result.message || "Registration failed.";
    }
  } catch (error) {
    console.error("Registration error:", error);
    alert("Failed to connect to server during registration.");
  }
}

// ✅ Submit Invoice Function (with auto logout after successful submission)
async function submitInvoice() {
  const invoiceNumber = document.getElementById("invoice-number").value.trim();
  const invoiceDate = document.getElementById("invoice-date").value.trim();
  const companyName = document.getElementById("company-name").value.trim();
  const contactPerson = document.getElementById("contact-person").value.trim();
  const companyPhone = document.getElementById("company-phone").value.trim();
  const items = document.getElementById("items").value.trim();
  const totalAmount = document.getElementById("total-amount").value.trim();
  const username = document.getElementById("user").value.trim();
  const userPhone = document.getElementById("phone").value.trim();

  if (!invoiceNumber || !invoiceDate || !companyName || !contactPerson || !companyPhone || !items || !totalAmount || !username || !userPhone) {
    alert("Please fill in all fields.");
    return;
  }

  if (!isValidPhone(companyPhone) || !isValidPhone(userPhone)) {
    alert("Phone numbers must be in +2547XXXXXXXX format.");
    return;
  }

  const invoiceText = `
INVOICE
Invoice Number: ${invoiceNumber}
Invoice Date: ${invoiceDate}

Bill To:
Company: ${companyName}
Contact Person: ${contactPerson}
Phone: ${companyPhone}

Items:
${items}

Total Amount: ${totalAmount}
`;

  if (!isValidInvoice(invoiceText)) {
    alert("Invalid invoice structure. Please check the fields.");
    return;
  }

  try {
    const res = await fetch(`${API_URL}/submit-invoice`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invoice: invoiceText, user: username, phone: userPhone })
    });
    const result = await res.json();

    if (result.error && result.error.includes("Invoice already exists")) {
      alert("Error: Invoice already exists!");
    } else if (result.message) {
      alert("Invoice submitted successfully! Redirecting to login...");
      setTimeout(() => {
        logout();  // ✅ Auto logout after 3 seconds
      }, 3000);
    } else {
      alert("An unexpected error occurred during invoice submission.");
    }
  } catch (error) {
    console.error("Submit invoice error:", error);
    alert("Failed to connect to server during invoice submission.");
  }
}

// ✅ Verify Invoice Function
async function verifyInvoice() {
  const invoice = document.getElementById("verify-text").value.trim();

  if (!invoice) {
    alert("Invoice text required.");
    return;
  }

  try {
    const res = await fetch(`${API_URL}/verify-invoice`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invoice })
    });
    const result = await res.json();
    document.getElementById("response-box").innerText = JSON.stringify(result, null, 2);
  } catch (error) {
    console.error("Verify invoice error:", error);
    alert("Failed to verify invoice.");
  }
}

// ✅ Logout Function
function logout() {
  window.location.href = "index.html";  // Redirect to login page
}

