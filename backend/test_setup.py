#!/usr/bin/env python3
"""
Quick test script - Verifica se o bot esta configurado corretamente
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    print("Testing imports...")
    try:
        from app.config import settings
        print("  [OK] Config loaded")
        from app.database import engine, Base, SessionLocal
        print("  [OK] Database configured")
        from app.auth import get_password_hash, verify_password
        print("  [OK] Auth functions OK")
        from app.clients.binance_client import BinanceFuturesClient
        print("  [OK] Binance client OK")
        from app.trading.engine import TradingEngine
        print("  [OK] Trading engine OK")
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def test_database():
    print("\nTesting database...")
    try:
        from app.database import engine, Base
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  [OK] Database connection OK")
        return True
    except Exception as e:
        print(f"  [FAIL] DB Error: {e}")
        return False

def test_admin_user():
    print("\nTesting admin user...")
    try:
        from app.database import SessionLocal
        from app import crud
        db = SessionLocal()
        user = crud.get_user_by_email(db, "admin@tradingbot.com")
        if user:
            print(f"  [OK] Admin user exists: {user.email}")
            print(f"      Role: {user.role}")
            print(f"      Subscription: {user.subscription_status}")
            db.close()
            return True
        else:
            print("  [FAIL] Admin user not found")
            db.close()
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def main():
    print("=" * 50)
    print("Binance Futures Bot - System Check")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_database())
    results.append(test_admin_user())
    
    print("=" * 50)
    if all(results):
        print("[OK] ALL CHECKS PASSED")
        print("\nYou can now start the bot:")
        print("  uvicorn app.main:app --reload --port 8000")
        print("\nOr run: start_bot.bat")
    else:
        print("[FAIL] SOME CHECKS FAILED")
        print("Review errors above and fix them.")
    print("=" * 50)

if __name__ == "__main__":
    main()
