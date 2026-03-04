# Habit Tracker API

This repository contains the backend implementation for a scalable and robust Habit Tracker. Built using Python, FastAPI, and PostgreSQL.

## Features Included
- **Authentication**: JWT token-based auth with hashed passwords
- **Habits API**: Complete CRUD functionalities for habits, including custom validation and tracking rules.
- **Habit Logs API**: Daily tracking with seamless Upsert logic (`ON CONFLICT` strategy on Postgres) to ensure minimal roundtrips and zero duplicate logs.
- **Database Architecture**: Managed via SQLAlchemy relationships and eager loading options.
- **Data Validation**: Strict type-checking using Pydantic V2 schemas.

## Requirements
- Python 3.10+
- PostgreSQL database

## Setup Instructions

1. **Activate Virtual Environment** (If not already active)
```bash
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Database Settings**
By default, the application connects to PostgreSQL using the following URL string config:
`postgresql://postgres:postgres@localhost:5432/habittracker`

Set your environment variables to override the credentials.
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/your_db_name"
export SECRET_KEY="your-jwt-secret-key"
```

4. **Initialize Database using Alembic Migrations**
The Alembic system has already been initialized and configured. To apply the initial structure to your new database, run:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Server
Run the local development server using uvicorn. Note since our app definition moved to the `app/` structure, we point uvicorn to `app.main:app`.
```bash
uvicorn app.main:app --reload
```

Your swagger API docs will be ready at:
`http://127.0.0.1:8000/api/v1/openapi.json`
`http://127.0.0.1:8000/docs`
