"""Vercel Python Serverless Function entry point.
Wraps the existing FastAPI app using Mangum for Vercel's Lambda‑compatible runtime.
"""

from mangum import Mangum
from app.main import app  # FastAPI instance

# Vercel expects a callable named `handler`
handler = Mangum(app)
