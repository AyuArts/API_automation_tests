# GoRest API Automation Tests

End‑to‑end regression suite for the **GoRest** public API, built with **Python 3.11**, **Pytest** and Playwright’s *
*`APIRequestContext`**.

---

## Tech Stack

| Category        | Tool                                  |
|-----------------|---------------------------------------|
| Language        | Python 3.11                           |
| Test Runner     | Pytest 8.x                            |
| HTTP Client     | Playwright 1.51 (`APIRequestContext`) |
| Data Generation | Faker                                 |
| Validation      | Pydantic 2.x models                   |
| Logging         | Loguru                                |
| Reporting       | Allure 2.x                            |
| Dependency Mgmt | Poetry                                |

---

## Project Layout

```text
.
├── clients/         # thin API clients wrapping HTTP verbs
│   ├── user_client.py
│   ├── post_client.py
│   └── comment_client.py
├── core/            # request factory, logger, mix‑ins, helpers
│   ├── base_clients.py
│   ├── decorators.py
│   └── logger.py
├── models/          # Pydantic response schemas
│   ├── user.py
│   ├── post.py
│   └── comment.py
├── tests/           # pytest scenarios (positive + negative)
│   ├── test_user.py
│   ├── test_post.py
│   └── test_comment.py
├── config.py        # global settings (base URL, token, timeouts…)
├── template.env     # sample env‑vars (copy → .env)
└── pyproject.toml   # Poetry deps
```

---

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/AyuArts/API_automation_tests.git
cd API_automation_tests

# 2. Install Poetry (if you haven’t yet)
pip install --upgrade poetry

# 3. Install dependencies
poetry install

# 4. Configure secrets
cp template.env .env   # fill GO_REST_TOKEN, etc.

# 5. (optional) activate venv
poetry shell
```

> **Prerequisites:** any modern Python 3.11+ interpreter — no browser is required because Playwright sends pure HTTP
> requests.

---

## Running Tests

```bash
# All tests with Allure output
pytest -q --alluredir=reports
allure serve reports

# Run a selected test class
pytest tests/test_user.py::TestUserClient -q

# Repeat failing tests until they pass (max 3 attempts)
pytest -q --reruns 3
```

Environment‑specific values (token, base URL) are injected via **pydantic‑settings** from your `.env` file.

---

## Test Scenarios (high‑level)

| #            | Endpoint              | Positive cases                             | Negative / Edge cases                       |
|--------------|-----------------------|--------------------------------------------|---------------------------------------------|
| **Users**    | `/public/v2/users`    | create, read, update, delete, list, filter | missing fields, duplicate email, invalid ID |
| **Posts**    | `/public/v2/posts`    | create, read, update, delete, list         | empty / too‑long / null title               |
| **Comments** | `/public/v2/comments` | create, read, list                         | empty name/body, invalid / empty email      |

> **Detailed, step‑by‑step checks** are provided in the companion document **[TEST_PLAN.md](./TEST_PLAN.md)**.

---

## Handy Poetry Commands

| Command                | Purpose                         |
|------------------------|---------------------------------|
| `poetry run pytest`    | Run tests inside the virtualenv |
| `poetry add <pkg>`     | Add a dependency                |
| `poetry update`        | Refresh lock‑file               |
| `poetry version patch` | Bump project version            |

---

## Contributing

Pull requests and issues are welcome! Please follow the **Angular commit style** (`feat:`, `fix:`, `test:` …).

---

> Happy API testing — may your endpoints always return **200 OK**!

