import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from arya_auth.config import AuthConfig
from arya_auth.security import get_password_hash
from datetime import datetime

async def seed_user():
    print("--- ARYA Auth Seeder ---")
    client = AsyncIOMotorClient(AuthConfig.MONGO_URI)
    db = client[AuthConfig.DB_NAME]
    
    email = "abhijeetmishralyff@gmail.com"
    password = "AbhijeetMishra001"
    
    # Check if user exists
    existing = await db.users.find_one({"email": email})
    if existing:
        print(f"User {email} already exists. Updating password...")
        await db.users.update_one(
            {"email": email},
            {"$set": {"hashed_password": get_password_hash(password)}}
        )
    else:
        print(f"Creating new user: {email}")
        await db.users.insert_one({
            "email": email,
            "hashed_password": get_password_hash(password),
            "created_at": datetime.utcnow()
        })
    
    print("User seeded successfully.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_user())
