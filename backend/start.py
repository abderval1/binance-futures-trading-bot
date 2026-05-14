#!/usr/bin/env python3
"""
Simple server starter - works on Windows without admin rights
"""
import sys
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  Binance Futures Trading Bot - Backend")
print("=" * 60)
print()
print("Starting server...")
print("  URL: http://0.0.0.0:8000")
print("  Docs: http://localhost:8000/docs")
print("  Health: http://localhost:8000/health")
print()
print("Press CTRL+C to stop")
print("=" * 60)
print()

# Import and run uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
