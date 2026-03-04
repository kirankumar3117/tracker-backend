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
- Google Cloud Project (for OAuth Client ID)

## Setup Instructions

1. **Activate Virtual Environment** (If not already active)
```bash
python -m venv venv
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create a `.env` file in the root directory and add:
```env
# Database connection string
DATABASE_URL=postgresql://tracker_user:tracker_password@localhost:5433/tracker_db

# JWT Secret Key (generate a strong one for production)
SECRET_KEY=your-super-secret-jwt-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

4. **Initialize Database using Alembic Migrations**
Apply all migrations to create the database tables (including auth_provider for Google OAuth support):
```bash
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
