# GoRest API – Detailed Test Plan

> **Scope:** Functional and negative testing of the `/public/v2` endpoints `users`, `posts`, `comments` using the
> Python + Playwright framework found in this repository.

---

## Table of Contents

1. [Users](#1-users)
2. [Posts](#2-posts)
3. [Comments](#3-comments)

---

## 1 · Users

| ID    | Title                                | Method   | Endpoint                   |
|-------|--------------------------------------|----------|----------------------------|
| U‑001 | Create valid user                    | `POST`   | `/users`                   |
| U‑002 | Create user – missing required field | `POST`   | `/users`                   |
| U‑003 | Retrieve existing user               | `GET`    | `/users/{id}`              |
| U‑004 | Retrieve non‑existent user           | `GET`    | `/users/{id}`              |
| U‑005 | Update user data                     | `PUT`    | `/users/{id}`              |
| U‑006 | Delete user                          | `DELETE` | `/users/{id}`              |
| U‑007 | List users (default)                 | `GET`    | `/users`                   |
| U‑008 | List users – pagination              | `GET`    | `/users?per_page=5&page=2` |

### Execution Steps & Checks Steps & Checks

<details>
<summary><strong>U‑001 · Create valid user</strong></summary>

1. **Prepare** random valid payload (<code>RandomUser.valid()</code> helper).
2. **Send** <code>POST /users</code>.
3. **Expect** response status **201**.
4. **Validate** body against <code>UserResponse</code> schema.
5. **Assert** that all submitted fields (name, gender, status, email) are echoed back.

</details>

<details>
<summary><strong>U‑002 · Create user – missing required field</strong></summary>

1. **Prepare** payload with empty <code>name=""</code>.
2. **POST /users** → expect **422**.
3. **Assert** error array contains `{field: "name", message: "can't be blank"}`.

</details>

*(… Similarly for U‑003 – U‑011; see <code>tests/test_user.py</code>)*

---

## 2 · Posts

| ID    | Title                        | Method   | Endpoint      |
|-------|------------------------------|----------|---------------|
| P‑001 | Create post                  | `POST`   | `/posts`      |
| P‑002 | Create post – empty title    | `POST`   | `/posts`      |
| P‑003 | Create post – too‑long title | `POST`   | `/posts`      |
| P‑004 | Create post – title None     | `POST`   | `/posts`      |
| P‑005 | Read post                    | `GET`    | `/posts/{id}` |
| P‑006 | Update post title            | `PATCH`  | `/posts/{id}` |
| P‑007 | Delete post                  | `DELETE` | `/posts/{id}` |

*(Detailed steps mirror the Users section; each negative case asserts **422** with the correct error message.)*

---

## 3 · Comments · Comments

| ID    | Title                                          | Method | Endpoint                  |
|-------|------------------------------------------------|--------|---------------------------|
| C‑001 | Add comment                                    | `POST` | `/comments`               |
| C‑002 | Add comment – empty <code>name</code>          | `POST` | `/comments`               |
| C‑003 | Add comment – invalid email                    | `POST` | `/comments`               |
| C‑004 | Add comment – empty email                      | `POST` | `/comments`               |
| C‑005 | Add comment – empty body                       | `POST` | `/comments`               |
| C‑006 | Read comment                                   | `GET`  | `/comments/{id}`          |
| C‑007 | List comments                                  | `GET`  | `/comments`               |
| C‑008 | List comments – filter by <code>post_id</code> | `GET`  | `/comments?post_id={pid}` |

### Example Negative Case (C‑003)

1. **Generate** comment with <code>email="invalid@"</code> (helper: <code>RandomComment(...,
   error_type=EmailError.INVALID)</code>).
2. **POST /comments** → expect **422**.
3. **Assert** error item `{field: "email", message: "is invalid"}` present.

---

## Traceability Matrix

| Scenario ID  | Automated Test | File / Function                         |
|--------------|----------------|-----------------------------------------|
| U‑001 …U‑008 | ✔              | `tests/test_user.py::TestUserClient`    |
| P‑001 …P‑007 | ✔              | `tests/test_post.py::TestPostClient`    |
| C‑001 …C‑008 | ✔              | `tests/test_comment.py::TestCommentAPI` |

---

> Last updated: **01 May 2025** – keep this file in sync with code changes.

