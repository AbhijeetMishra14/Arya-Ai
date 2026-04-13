from motor.motor_asyncio import AsyncIOMotorClient
from arya_auth.config import AuthConfig

class DatabaseManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None

neural_db = DatabaseManager()

async def connect_to_mongo():
    neural_db.client = AsyncIOMotorClient(AuthConfig.MONGO_URI)
    neural_db.db = neural_db.client[AuthConfig.DB_NAME]
    print(f"Connected to MongoDB: {AuthConfig.DB_NAME}")

async def close_mongo_connection():
    if neural_db.client:
        neural_db.client.close()
    print("Closed MongoDB connection")
