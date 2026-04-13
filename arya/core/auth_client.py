import requests
import socket
import uuid
import os
import json
import platform
from datetime import datetime

class AuthClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.user_email = None
        self.user_data = None # Storage for GUI session
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "auth_config.json")
        self._load_session()

    def _get_device_id(self):
        try:
            import platform, uuid, socket
            # Create a fingerprint from hostname + CPU ID + MAC
            node = uuid.getnode()
            fingerprint = f"{socket.gethostname()}-{platform.processor()}-{node}"
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, fingerprint))
        except:
            import uuid
            return str(uuid.uuid4())

    def _load_session(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.token = data.get("token")
                    self.user_email = data.get("email")
            except: pass

    def _save_session(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump({"token": self.token, "email": self.user_email}, f)
        except: pass

    def is_logged_in(self):
        return self.token is not None

    def signup(self, email, password):
        try:
            resp = requests.post(f"{self.base_url}/signup", json={"email": email, "password": password}, timeout=5)
            if resp.status_code == 200:
                return True, "Account created. You can now link this device."
            return False, resp.json().get("detail", "Registration failed.")
        except Exception as e: return False, str(e)

    def login(self, email, password):
        try:
            resp = requests.post(f"{self.base_url}/login", json={"username": email, "password": password}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data["access_token"]
                self.user_email = email
                self.user_data = {"email": email}
                self._save_session()
                return True, "Neural Link established."
            return False, "Invalid credentials or server rejected link."
        except Exception as e: return False, str(e)

    def logout(self):
        self.token = None
        self.user_email = None
        if os.path.exists(self.config_path):
            try: os.remove(self.config_path)
            except: pass

    def register_this_device(self):
        if not self.is_logged_in(): return False
        try:
            from arya.modules.device_info import LocalDeviceSystem
            sys_info = LocalDeviceSystem()
            profile = sys_info.get_static_profile()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "device_id": self._get_device_id(),
                "device_name": socket.gethostname(),
                "device_type": "PC",
                "profile": profile,
                "status": sys_info.get_live_pulse()
            }
            resp = requests.post(f"{self.base_url}/devices", json=data, headers=headers, timeout=5)
            return resp.status_code == 200
        except: return False

    def send_heartbeat(self, payload: dict = None):
        if not self.is_logged_in(): return
        try:
            if payload is None:
                from arya.modules.device_info import LocalDeviceSystem
                payload = LocalDeviceSystem().get_live_pulse()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            did = self._get_device_id()
            requests.patch(f"{self.base_url}/devices/{did}", json={"status": payload}, headers=headers, timeout=5)
        except: pass


    def send_remote_action(self, target_id: str, command: str, payload: dict = {}):
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {"command": command, "payload": payload}
            resp = requests.post(f"{self.base_url}/devices/{target_id}/actions", json=data, headers=headers, timeout=5)
            return resp.status_code == 200
        except: return False

    def poll_remote_actions(self):
        if not self.is_logged_in(): return []
        try:
            did = self._get_device_id()
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/devices/actions/pending", headers=headers, timeout=5)
            if resp.status_code == 200:
                all_pending = resp.json()
                return [a for a in all_pending if a.get("target_device_id") == did]
            return []
        except: return []

    def complete_remote_action(self, action_id: str, status: str, result: str):
        """Signals to the neural cloud that a specific remote command has been executed. status: 'success' or 'failed'."""
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {"status": status, "result": result}
            resp = requests.patch(f"{self.base_url}/devices/actions/{action_id}", json=data, headers=headers, timeout=5)
            return resp.status_code == 200
        except: return False

    def sync_clipboard(self, text: str):
        if not self.is_logged_in(): return False
        try:
            did = self._get_device_id()
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{self.base_url}/continuity/clipboard", json={"text": text, "device_id": did}, headers=headers, timeout=2)
            return resp.status_code == 200
        except: return False

    def get_remote_clipboard(self):
        if not self.is_logged_in(): return None
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/continuity/clipboard", headers=headers, timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("source") != self._get_device_id():
                    return data.get("text")
            return None
        except: return None

    def upload_file(self, target_id: str, file_path: str):
        if not self.is_logged_in() or not os.path.exists(file_path): return False
        try:
            did = self._get_device_id()
            headers = {"Authorization": f"Bearer {self.token}"}
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                params = {"target_device_id": target_id, "sender_device_id": did}
                files = {"file": (file_name, f)}
                resp = requests.post(f"{self.base_url}/continuity/files/upload", params=params, files=files, headers=headers, timeout=60)
                return resp.status_code == 200
        except: return False

    def get_incoming_files(self):
        if not self.is_logged_in(): return []
        try:
            did = self._get_device_id()
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/continuity/files/pending", headers=headers, timeout=5)
            if resp.status_code == 200:
                all_transfers = resp.json()
                return [t for t in all_transfers if t.get("receiver_device_id") == did]
            return []
        except: return []

    def download_file(self, transfer_id: str, save_path: str):
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/continuity/files/download/{transfer_id}", headers=headers, stream=True, timeout=60)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                # Clear after download
                requests.delete(f"{self.base_url}/continuity/files/{transfer_id}", headers=headers)
                return True
            return False
        except: return False

    def purge_ecosystem_nodes(self):
        """Clears all devices from your account ecosystem. Use this for a fresh start or to remove stale nodes."""
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.delete(f"{self.base_url}/devices/all", headers=headers, timeout=5)
            if resp.status_code == 200:
                self.register_this_device() # Auto-relink THIS device
                return True
            return False
        except: return False

    def update_device_nickname(self, device_id: str, nickname: str):
        """Assigns a custom nickname to a specific node in your ARYA ecosystem."""
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.patch(f"{self.base_url}/devices/{device_id}", json={"nickname": nickname}, headers=headers, timeout=5)
            return resp.status_code == 200
        except: return False

    def get_automation_rules(self):
        if not self.is_logged_in(): return []
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/automations", headers=headers, timeout=5)
            return resp.json() if resp.status_code == 200 else []
        except: return []

    def save_automation_rule(self, rule_data: dict):
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.post(f"{self.base_url}/automations", json=rule_data, headers=headers, timeout=5)
            return resp.status_code == 200
        except: return False

    def delete_automation_rule(self, rule_id: str):
        if not self.is_logged_in(): return False
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.delete(f"{self.base_url}/automations/{rule_id}", headers=headers, timeout=5)
            return resp.status_code == 200
        except: return False

    def get_action_status(self, action_id: str):
        if not self.is_logged_in(): return "unknown"
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/devices/actions/{action_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json().get("status", "unknown")
            return "unknown"
        except: return "error"

    def get_action_history(self, device_id: str):
        if not self.is_logged_in(): return []
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/devices/{device_id}/history", headers=headers, timeout=5)
            return resp.json() if resp.status_code == 200 else []
        except: return []

    def resolve_device_id(self, name_query: str):
        """Fuzzy match device by nickname, hostname, or model."""
        if not self.is_logged_in(): return None
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            resp = requests.get(f"{self.base_url}/devices", headers=headers, timeout=5)
            if resp.status_code == 200:
                devices = resp.json()
                q = name_query.lower().strip()
                
                # 1. Exact Nickname match
                for d in devices:
                    if d.get("nickname") and d["nickname"].lower() == q: return d["device_id"]
                
                # 2. Exact Hostname match
                for d in devices:
                    if d["device_name"].lower() == q: return d["device_id"]
                
                # 3. Fuzzy match
                for d in devices:
                    if q in d["device_name"].lower() or (d.get("nickname") and q in d["nickname"].lower()):
                        return d["device_id"]
            return None
        except: return None
