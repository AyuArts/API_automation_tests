# 📋 GoRest API Test Plan

---

## 👤 User API Tests – `/public/v2/users`

### **Test 0** – Create a new user

**Check:**

- ✅ Response code: `201 Created`
- ✅ Response body contains user ID and correct user details

---

### **Test 1** – Get user by ID

**Check:**

- ✅ Response code: `200 OK`
- ✅ Response body matches the created user data

---

### **Test 2** – Update user information

**Check:**

- ✅ Response code: `200 OK`
- ✅ Updated fields are reflected in the response

---

### **Test 3** – Delete user

**Check:**

- ✅ Response code: `204 No Content`
- ✅ Trying to get deleted user returns `404 Not Found`

---

### **Test 4** – Create user with missing fields

**Check:**

- ✅ Response code: `422 Unprocessable Entity`
- ✅ Error messages indicate which fields are missing

---

### **Test 5** – Create user with duplicate email

**Check:**

- ✅ Response code: `422 Unprocessable Entity`
- ✅ Error message about email already being taken

---

### **Test 6** – Get list of users with pagination

**Check:**

- ✅ Response code: `200 OK`
- ✅ Response body contains multiple users

---

### **Test 7** – Filter users by gender or status

**Check:**

- ✅ Response code: `200 OK`
- ✅ Only users matching the filter are returned

---

### **Test 8** – Get user with invalid ID

**Check:**

- ✅ Response code: `404 Not Found`
- ✅ Proper error message in the response

---

## 📅 Post API Tests – `/public/v2/posts`

### **Test 0** – Create a post for a user

**Check:**

- ✅ Response code: `201 Created`
- ✅ Post is linked to the correct user ID

---

### **Test 1** – Get post by ID

**Check:**

- ✅ Response code: `200 OK`
- ✅ Post details match the created content

---

### **Test 2** – Update a post

**Check:**

- ✅ Response code: `200 OK`
- ✅ Changes are reflected correctly

---

### **Test 3** – Delete a post

**Check:**

- ✅ Response code: `204 No Content`
- ✅ Retrieving deleted post returns `404 Not Found`

---

### **Test 4** – Create a post without required fields

**Check:**

- ✅ Response code: `422 Unprocessable Entity`
- ✅ Proper validation error message

---

## 💬 Comment API Tests – `/public/v2/comments`

### **Test 0** – Create a comment for a post

**Check:**

- ✅ Response code: `201 Created`
- ✅ Comment is linked to the correct post ID

---

### **Test 1** – Get comment by ID

**Check:**

- ✅ Response code: `200 OK`
- ✅ Comment details match the created data

---

### **Test 2** – Update a comment

**Check:**

- ✅ Response code: `200 OK`
- ✅ Changes are reflected correctly

---

### **Test 3** – Delete a comment

**Check:**

- ✅ Response code: `204 No Content`
- ✅ Retrieving deleted comment returns `404 Not Found`

---

### **Test 4** – Create comment without required fields

**Check:**

- ✅ Response code: `422 Unprocessable Entity`
- ✅ Proper validation error message

---

## 🔐 Authorization and Token Tests

### **Test 0** – Send request without Authorization token

**Check:**

- ✅ Response code: `401 Unauthorized`
- ✅ Error message about missing or invalid token

---

### **Test 1** – Send request with invalid Authorization token

**Check:**

- ✅ Response code: `401 Unauthorized`
- ✅ Proper error handling without server crash

---

# ✅ **Summary:**

- 9 User API tests
- 5 Post API tests
- 5 Comment API tests
- 2 Authorization tests

🔹 **Total: 21 structured API test scenarios**

