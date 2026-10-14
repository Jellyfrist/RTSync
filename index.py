"""FastAPI entrypoint for Vercel (backend project root: repository root).

Keep the application factory and all API routes in app/main.py.
Local development can continue to use: uvicorn app.main:app --reload --port 8001
"""

from app.main import app
