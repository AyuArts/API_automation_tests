# 📋 Petstore API Test Plan

---

# 🐾 Pet API Tests – `POST /pet/{petId}/uploadImage`

### **Test #0** – Upload valid `.jpg` file

**Check:**

- ✅ Response code is **200 OK**
- ✅ Response body contains confirmation of upload (e.g., `"uploaded"` or file info)

---

### **Test #1** – Upload request without file

**Check:**

- ✅ Response code is **200 OK** or **400 Bad Request**
- ✅ Error message or explanation about missing file

---

### **Test #2** – Upload with invalid `petId`

**Check:**

- ✅ Response code is **400 Bad Request** or **404 Not Found**
- ✅ No internal server error or crash

---

### **Test #3** – Upload file with invalid format (e.g., `.exe`)

**Check:**

- ✅ Response code is **400 Bad Request**
- ✅ Error message describes unsupported file type

---

### **Test #4** – Upload with SQL Injection payload (e.g., filename: `' OR '1'='1.jpg`)

**Check:**

- ✅ Response code is **200 OK** or **400 Bad Request**
- ✅ Server does **not** crash or leak data

---

### **Test #5** – Upload file simulating XSS attack (e.g., `.html` with `<script>`)

**Check:**

- ✅ Response code is **200 OK** or **400 Bad Request**
- ✅ Uploaded content is **not executed** or returned unsanitized

---

### **Test #6** – Stress test with multiple parallel uploads

**Check:**

- ✅ Server remains stable under load
- ✅ No **5xx** errors or slowdowns

---

### **Test #7** – Upload large file (~5 MB)

**Check:**

- ✅ Response code is **200 OK**, or
- ✅ Response code is **413 Payload Too Large** if server limits exceeded

---

### **Test #8** – Upload tiny file (1 byte)

**Check:**

- ✅ Response code is **200 OK**
- ✅ File is accepted or rejected with clear reason

---

### **Test #9** – Upload file with special characters in filename

**Check:**

- ✅ Response code is **200 OK**
- ✅ File name is handled safely (no path traversal, encoding issues)

---

# 👤 User API Tests – `/user`

### **Test #0** – Create new user

**Check:**

- ✅ Response code is **200 OK**
- ✅ Message contains user ID

---

### **Test #1** – Get created user

**Check:**

- ✅ Response code is **200 OK**
- ✅ Correct user data is returned

---

### **Test #2** – Login with correct credentials

**Check:**

- ✅ Response code is **200 OK**
- ✅ Response includes login session/token

---

### **Test #3** – Logout user

**Check:**

- ✅ Response code is **200 OK**
- ✅ Confirmation message is returned

---

### **Test #4** – Login with wrong password

**Check:**

- ✅ Response code is **400 Bad Request**
- ✅ Error message explains the failure

---

### **Test #5** – Create user missing required field

**Check:**

- ✅ Response code is **400 Bad Request**
- ✅ Message indicates which field is missing

---

### **Test #6** – Update user info

**Check:**

- ✅ Response code is **200 OK**
- ✅ Changes are applied successfully

---

### **Test #7** – Get updated user

**Check:**

- ✅ Response code is **200 OK**
- ✅ Updated fields match submitted data

---

### **Test #8** – Delete user

**Check:**

- ✅ Response code is **200 OK**
- ✅ User is no longer accessible

---

### **Test #9** – Get deleted user

**Check:**

- ✅ Response code is **404 Not Found**
- ✅ Message indicates user does not exist

---

# 🏬 Store API Tests – `/store`

### **Test #0** – Place new order

**Check:**

- ✅ Response code is **200 OK**
- ✅ Response includes correct order data

---

### **Test #1** – Get placed order

**Check:**

- ✅ Response code is **200 OK**
- ✅ Order details match the request

---

### **Test #2** – Delete placed order

**Check:**

- ✅ Response code is **200 OK**
- ✅ Order is removed successfully

---

### **Test #3** – Get deleted order

**Check:**

- ✅ Response code is **404 Not Found**
- ✅ Message explains the order is missing

---

### **Test #4** – Place order missing fields

**Check:**

- ✅ Response code is **400 Bad Request**
- ✅ Clear validation error message

---

### **Test #5** – Get store inventory

**Check:**

- ✅ Response code is **200 OK**
- ✅ Response body is a dictionary

---

### **Test #6** – Check inventory statuses

**Check:**

- ✅ Status keys like `sold`, `available`, `pending` are present
- ✅ Values are valid integers

---

### **Test #7** – Place order with very large quantity

**Check:**

- ✅ Response code is **200 OK** (if allowed), or
- ✅ Appropriate limit error is returned

---

### **Test #8** – Delete non-existing order

**Check:**

- ✅ Response code is **404 Not Found**
- ✅ Error message describes the issue

---

### **Test #9** – Stress test placing orders

**Check:**

- ✅ Server remains stable under load
- ✅ Most requests succeed (no 5xx)

# ✅ Total:

- 10 тестов на **Pet API**
- 10 тестов на **User API**
- 10 тестов на **Store API**