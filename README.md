# UWO Patent Website — Backend API (FastAPI)

Backend API for a Western University–branded website that lets users search inactive U.S. patents.  
Frontend (Next.js) will be in a different directory

## Tech
- Python 3.11+, FastAPI, SQLAlchemy
- SQLite for local dev (Postgres in prod)
- Open-source license: **GNU GPL v3**

## Run (local)
```bash
python -m venv .venv
source .venv/bin/activate           
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
uvicorn server:app --reload