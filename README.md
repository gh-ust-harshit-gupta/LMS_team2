
# PAY CREST – Loan Management System (Backend)

FastAPI + MongoDB (Motor) backend implementing authentication, RBAC, KYC, loan workflows, and transactions.

## Features
- Async FastAPI routers and service layer
- MongoDB Motor async driver
- JWT auth (PyJWT) + bcrypt password hashing
- Role-based access control
- Customer registration auto-creates a bank account
- KYC submission & verification scoring
- Personal & Vehicle loan application and workflow
- EMI payments with balance deduction & CIBIL updates
- Admin settings management (interest rates, min CIBIL)

## Project Structure
```
app/
 ├── main.py
 ├── database/mongo.py
 ├── core/
 │    ├── config.py
 │    └── security.py
 ├── models/enums.py
 ├── schemas/
 ├── routers/
 ├── services/
 └── utils/
```

## Quick Start
1. **Create and configure environment**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # edit .env with your secrets and DB URI
   ```

2. **Run server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment (.env)
See `.env.example` for defaults.

## Notes
- Ensure an admin user exists (manually insert into `users` with role `admin`).
- Account numbers are generated using `counters` collection starting at `1000000001`.
- EMI calculation uses standard formula for approximate monthly dues.
- Adjust scoring and workflow to your compliance requirements.
