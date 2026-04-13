from pymongo import MongoClient
import datetime
import traceback
from arya.core.config import Config
import certifi

class Memory:
    """Handles long-term persistence strictly using MongoDB."""
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.contacts = None
        
        if Config.MONGO_URI:
            try:
                # Elite Connection Protocol: Targeted DB + SSL Certification
                self.client = MongoClient(
                    Config.MONGO_URI, 
                    serverSelectionTimeoutMS=5000,
                    tlsCAFile=certifi.where() # Ensure SSL handshakes succeed on all networks
                )
                self.client.server_info() # Validate link
                self.db = self.client['arya_db']
                self.collection = self.db['conversations']
                self.contacts = self.db['contacts']
                self.preferences = self.db['preferences']
                print("[SYSTEM]: ARYA Neural Database is ONLINE and synchronized.")
            except Exception as e:
                print(f"[SYSTEM CRITICAL]: Neural link to MongoDB failed: {e}")
                self.client = None

    def get_recent_history(self, limit=10):
        if self.collection is not None:
            try:
                docs = list(self.collection.find().sort("timestamp", -1).limit(limit))
                history = []
                for doc in reversed(docs):
                    history.append({"role": "user", "parts": [doc["user"]]})
                    history.append({"role": "model", "parts": [doc["arya"]]})
                return history
            except:
                pass
        return []
        
    def save_contact(self, name: str, phone: str = "", email: str = "", relationship: str = "", notes: str = "") -> str:
        """Saves or updates a contact with provided details like phone or email."""
        details = {}
        if phone: details['phone'] = phone
        if email: details['email'] = email
        if relationship: details['relationship'] = relationship
        if notes: details['notes'] = notes
        
        if self.contacts is not None:
            lower_name = name.lower()
            # Ensure we keep existing fields if just updating
            existing = self.contacts.find_one({"name": lower_name}) or {}
            update_data = {**existing, **details, "name": lower_name, "original_name": name}
            
            self.contacts.update_one(
                {"name": lower_name},
                {"$set": update_data},
                upsert=True
            )
            fields = ", ".join([f"{k}: {v}" for k,v in details.items()])
            return f"Successfully saved to neural database for '{name}': {fields}"
        return "Database is offline. Unable to update contact."

    def get_contact_details(self, name: str) -> dict:
        """Retrieves all stored details (phone, email) for a contact."""
        if self.contacts is not None:
            contact = self.contacts.find_one({"name": name.lower()})
            if contact:
                return contact
        return {}

    def get_contact_email(self, name: str) -> str:
        """Retrieves the stored email address for a specific contact name."""
        details = self.get_contact_details(name)
        return details.get('email', f"Contact '{name}' not found.")

    def save_user_profile(self, name: str, profile_data: dict) -> bool:
        if self.db is not None:
            users_col = self.db['users']
            users_col.update_one(
                {"name": name},
                {"$set": profile_data},
                upsert=True
            )
            return True
        return False
        
    def get_user_profile(self, name: str) -> dict:
        if self.db is not None:
            return self.db['users'].find_one({"name": name}) or {}
        return {}
    def log_interaction(self, user_text: str, arya_response: str):
        if self.collection is not None:
            doc = {
                "timestamp": datetime.datetime.now(datetime.UTC),
                "user": user_text,
                "arya": arya_response
            }
            try:
                self.collection.insert_one(doc)
            except Exception as e:
                print(f"[DB Error] Failed to log interaction: {e}")

    def save_preference(self, key: str, value: any, category: str = "general"):
        """Saves a learned user preference or behavioral pattern."""
        if self.preferences is not None:
            self.preferences.update_one(
                {"key": key, "category": category},
                {"$set": {"value": value, "last_updated": datetime.datetime.now(datetime.UTC)}},
                upsert=True
            )

    def get_preferences(self, category: str = None) -> dict:
        """Retrieves learned preferences for a specific category or all."""
        if self.preferences is not None:
            query = {"category": category} if category else {}
            pairs = list(self.preferences.find(query))
            return {p['key']: p['value'] for p in pairs}
        return {}

    def get_contextual_sample(self, limit=30):
        """Retrieves a larger block of history for pattern analysis (not for direct prompt injection)."""
        if self.collection is not None:
            return list(self.collection.find().sort("timestamp", -1).limit(limit))
        return []
