import os
from dotenv import load_dotenv

load_dotenv()

class AuthConfig:
    SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "ARYA_NEURAL_TOKEN_X_777")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = "arya_ecosystem"
