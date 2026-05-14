#!/usr/bin/env python3
"""Start backend server"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Starting Binance Futures Trading Bot Backend...")
print("URL: http://0.0.0.0:8000")
print("Docs: http://localhost:8000/docs")
print("Press CTRL+C to stop")
print("-" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
