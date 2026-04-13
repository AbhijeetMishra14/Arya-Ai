import os
import sys
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    # PyInstaller securely places data files in _MEIPASS regardless of onedir/onefile
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

env_path = os.path.join(base_path, '.env')
load_dotenv(dotenv_path=env_path)

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY # Fallback binding for internal GenAI bugs
    
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    GMAIL_USER = os.getenv("GMAIL_USER")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    ROUTER_URL = os.getenv("ROUTER_URL", "http://192.168.18.1")
    ROUTER_USER = os.getenv("ROUTER_USER", "admin")
    ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD", "")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        
        if missing:
            print(f"Warning: Missing API keys in .env file: {', '.join(missing)}")
            return False
        return True
