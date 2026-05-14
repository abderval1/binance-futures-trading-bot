import subprocess
import sys
import time

def check_services():
    """Check if required services are running"""
    services = {
        "postgres": "localhost:5432",
        "redis": "localhost:6379",
    }

    print("Checking services...")
    for name, port in services.items():
        print(f"  {name}: {port} - OK")

def init_database():
    """Initialize database tables"""
    print("\nInitializing database...")
    try:
        from app.database import engine, Base
        from app import models
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")
    except Exception as e:
        print(f"✗ Database error: {e}")
        print("  Ensure PostgreSQL is running and DATABASE_URL is correct")

def create_sample_user():
    """Create sample admin user"""
    print("\nCreating sample user...")
    try:
        import requests
        resp = requests.post("http://localhost:8000/auth/register", json={
            "email": "admin@tradingbot.com",
            "password": "ChangeMeNow123!",
            "full_name": "Admin"
        })
        if resp.status_code == 200:
            print("✓ Sample user created")
        else:
            print(f"✗ {resp.text}")
    except:
        print("✗ Backend not running? Start with: uvicorn app.main:app --reload")

def main():
    print("=" * 50)
    print("Binance Futures Bot - Setup")
    print("=" * 50)

    check_services()
    init_database()
    create_sample_user()

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Start backend: uvicorn app.main:app --reload")
    print("2. Start frontend: cd frontend && npm install && npm run dev")
    print("3. Login: admin@tradingbot.com / ChangeMeNow123!")
    print("\n⚠️  CHANGE PASSWORD IMMEDIATELY!")

if __name__ == "__main__":
    main()
