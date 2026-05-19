#!/usr/bin/env python3
"""Start backend server - Fixed version"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  Binance Futures Trading Bot - Backend")
    print("=" * 60)
    print("Starting server...")
    print("  URL: http://0.0.0.0:8000")
    print("  Docs: http://localhost:8000/docs")
    print("  Health: http://localhost:8000/health")
    print("Press CTRL+C to stop")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
