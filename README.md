# 🏦 Banking API

A production-ready RESTful Banking API built with **Django REST Framework**, featuring async task processing with **Celery + RabbitMQ**, JWT authentication, and full Docker support.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0.3 + Django REST Framework |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Message Broker | RabbitMQ 3 |
| Task Queue | Celery 5 |
| Authentication | JWT (djangorestframework-simplejwt) |
| API Docs | drf-spectacular (Swagger / OpenAPI 3.0) |
| Containerization | Docker + Docker Compose |
| CI/CD | GitLab CI/CD |

---

## ✨ Features

- **JWT Authentication** — Register, login, logout with access + refresh tokens
- **Bank Account Management** — Create multiple accounts (savings, current)
- **Transactions** — Deposit, withdrawal, transfer with atomic DB operations
- **Async Notifications** — Celery tasks fire after every transaction via RabbitMQ
- **Transaction History** — Full audit trail per user
- **Race Condition Safe** — All transactions use `select_for_update` with atomic blocks
- **Auto API Docs** — Swagger UI at `/api/docs/`
- **9 Unit Tests** — Auth + transaction tests with mocked Celery tasks
- **CI/CD Pipeline** — Automated test + Docker build on every push

---

## 📁 Project Structure

```
banking-api/
├── accounts/           # User auth + BankAccount models
├── transactions/       # Deposit, withdrawal, transfer logic
├── notifications/      # Celery async notification tasks
├── banking_api/        # Django settings, URLs, Celery config
├── .gitlab-ci.yml      # GitLab CI/CD pipeline
├── docker-compose.yml  # Full local dev environment
├── Dockerfile
└── requirements.txt
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login + get JWT tokens |
| POST | `/api/auth/logout/` | Logout + blacklist token |
| GET | `/api/auth/profile/` | Get user profile |
| PUT | `/api/auth/profile/` | Update user profile |
| POST | `/api/auth/token/refresh/` | Refresh access token |

### Bank Accounts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/auth/bank-accounts/` | List user's accounts |
| POST | `/api/auth/bank-accounts/` | Create new bank account |
| GET | `/api/auth/bank-accounts/{id}/` | Get account details |

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/transactions/deposit/` | Deposit funds |
| POST | `/api/transactions/withdraw/` | Withdraw funds |
| POST | `/api/transactions/transfer/` | Transfer between accounts |
| GET | `/api/transactions/history/` | Transaction history |
| GET | `/api/transactions/{id}/` | Transaction detail |

---

## ⚙️ Local Setup

### Prerequisites
- Docker Desktop
- Python 3.12+

### 1. Clone the repo
```bash
git clone https://github.com/Nihal2999/banking-api.git
cd banking-api
```

### 2. Create `.env` file
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=True
DATABASE_URL=postgresql://postgres:password@postgres:5432/banking_db
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
```

### 3. Run with Docker
```bash
docker compose up --build
```

This starts:
- **Django app** at `http://localhost:8000`
- **Swagger docs** at `http://localhost:8000/api/docs/`
- **RabbitMQ UI** at `http://localhost:15672` (guest/guest)
- **PostgreSQL** at `localhost:5433`
- **Redis** at `localhost:6380`

---

## 🧪 Running Tests

```bash
# With Docker running
docker compose exec app python manage.py test

# Locally with venv
python manage.py test
```

---

## 🔄 CI/CD Pipeline

GitLab CI/CD runs on every push to `main`:

```
push to main
    │
    ├── test stage
    │     ├── Spin up PostgreSQL, Redis, RabbitMQ services
    │     ├── Run migrations
    │     └── Run 9 unit tests
    │
    └── build stage
          └── Build Docker image
```

---

## 💡 Key Technical Decisions

**Atomic Transactions** — All financial operations use `@transaction.atomic` with `select_for_update()` to prevent race conditions and ensure data consistency.

**Async Notifications** — Transaction notifications are decoupled from the main request using Celery tasks published to RabbitMQ, keeping API response times fast.

**Token Blacklisting** — Logout invalidates refresh tokens using `djangorestframework-simplejwt`'s token blacklist, preventing reuse after logout.

---

## 📸 Sample Request

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "Pass@1234", "password2": "Pass@1234"}'
```

**Deposit:**
```bash
curl -X POST http://localhost:8000/api/transactions/deposit/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "<account_id>", "amount": "5000.00", "description": "Initial deposit"}'
```

**Withdraw:**
```bash
curl -X POST http://localhost:8000/api/transactions/withdraw/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"account_id": "<account_id>", "amount": "1000.00", "description": "ATM withdrawal"}'
```

**Transfer:**
```bash
curl -X POST http://localhost:8000/api/transactions/transfer/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"from_account_id": "<account_id>", "to_account_id": "<account_id>", "amount": "500.00", "description": "Transfer test"}'
```