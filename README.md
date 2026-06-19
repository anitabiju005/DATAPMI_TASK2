# Task 2 – FastAPI Project Management Backend API

## Overview

This project is a backend REST API built using FastAPI for managing users and projects with authentication and role-based access control.

The application supports:

* JWT authentication
* Role-based authorization (`admin`, `manager`, `user`)
* Project CRUD operations
* Database migrations using Alembic
* Seed data generation for testing
* CORS configuration for frontend integration
* Async SQLAlchemy database support

---

## Tech Stack

* Python 3.x
* FastAPI
* SQLAlchemy (Async)
* SQLite
* Alembic
* JWT Authentication
* Pydantic
* Uvicorn

---

## Project Structure

```text
TASK2/
│
├── app/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   └── seed.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── alembic.ini
├── README.md
├── .gitignore
└── .env
```

---

## Features

### Authentication

* User login using email and password
* JWT access token generation
* Token-based authorization using Bearer authentication

### Role Based Access Control

Available roles:

* Admin
* Manager
* User

Access permissions can be restricted depending on the authenticated user's role.

### Project Management

Project fields:

* id
* title
* description
* status
* owner_id
* created_at
* updated_at

Available statuses:

* draft
* active
* completed
* archived

Supported operations:

* Create project
* Get all projects
* Get project by ID
* Update project
* Delete project

---

## Seed Data

Application startup automatically creates sample data:

### Users

Admin:

```text
Email: admin@test.com
Password: Admin@123
```

Manager:

```text
Email: manager@test.com
Password: Manager@123
```

User:

```text
Email: user@test.com
Password: User@123
```

### Projects

Five sample projects are automatically generated with different:

* owners
* statuses
* descriptions

This allows frontend development and testing without manual setup.

---

## Installation

Clone repository:

```bash
git clone <repository-url>
cd task2
```

Create virtual environment:

```bash
python -m venv task1
```

Activate environment:

Linux/macOS:

```bash
source task1/bin/activate
```

Windows:

```bash
task1\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env`

Example:

```env
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

---

## Database Migration

Create migration:

```bash
alembic revision --autogenerate -m "initial schema"
```

Apply migration:

```bash
alembic upgrade head
```

---

## Run Application

Start server:

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## Authentication Usage

1. Login:

```text
POST /api/v1/auth/login
```

Request:

```json
{
    "email":"admin@test.com",
    "password":"Admin@123"
}
```

Response:

```json
{
   "access_token":"<jwt-token>",
   "token_type":"bearer"
}
```

2. Copy the access token.

3. Click "Authorize" in Swagger.

4. Enter:

```text
Bearer <your-token>
```

---

## CORS Configuration

CORS is enabled for local frontend development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Frontend applications running on Vite can connect directly.

---

