import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

if __name__ == "__main__":
    print("Creating sample admin user...")
    # Run this after backend is running
    import requests

    response = requests.post(
        "http://localhost:8000/auth/register",
        json={
            "email": "admin@tradingbot.com",
            "password": "ChangeMeNow123!",
            "full_name": "Admin"
        }
    )

    if response.status_code == 200:
        print("✓ Admin user created successfully!")
        print(f"\n⚠️  SECURITY: Change these credentials immediately!")
        print(f"Email: admin@tradingbot.com")
        print(f"Password: ChangeMeNow123!")
        print("\nLogin at: http://localhost:5173/login")
    else:
        print(f"✗ Failed: {response.text}")
