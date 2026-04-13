import asyncio
from arya_auth.db import connect_to_mongo, neural_db
from arya_auth.auth_utils import get_password_hash

async def sync_identity():
    await connect_to_mongo()
    if neural_db.db is None:
        print("CRITICAL: Could not connect to MongoDB.")
        return
        
    email = "abhijeetmishralyff@gmail.com"
    hashed = get_password_hash("arya1234")
    
    await neural_db.db['users'].update_one(
        {"email": email},
        {"$set": {
            "email": email,
            "hashed_password": hashed,
            "master_node": True
        }},
        upsert=True
    )
    print(f"SUCCESS: Identity {email} is now fully migrated and active.")

if __name__ == "__main__":
    asyncio.run(sync_identity())
