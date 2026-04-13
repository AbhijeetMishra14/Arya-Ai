from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime = datetime.utcnow()

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- CONTINUITY MODELS ---

class ClipboardData(BaseModel):
    user_email: str
    text: str
    source_device_id: str
    updated_at: datetime = datetime.utcnow()

class FileTransfer(BaseModel):
    transfer_id: str
    sender_id: str
    target_id: str
    file_name: str
    file_size_mb: float
    status: str = "pending" # pending, completed, failed
    timestamp: datetime = datetime.utcnow()

class AutomationRule(BaseModel):
    rule_id: str
    name: str
    trigger_type: str # battery, charging, cpu, ram, wifi, time, app
    trigger_condition: str # <, >, ==, becomes_charging, disconnects
    trigger_value: Optional[str] = None
    action_type: str # notification, open_app, lock, volume, shutdown
    action_payload: Optional[dict] = {}
    is_active: bool = True
    last_triggered: Optional[datetime] = None

# --- TITAN-ELITE: Device Profile ---

class DeviceSpecs(BaseModel):
    model: str
    manufacturer: str
    os_name: str
    os_version: str
    cpu_model: str
    cpu_cores: int
    cpu_speed: str
    ram_gb: float
    gpu_name: str
    gpu_total_vram_gb: float
    storage: List[Dict]
    screen_res: str
    timezone: str
    first_linked: str

class DeviceLiveStatus(BaseModel):
    cpu_usage: float
    ram_usage: float
    ram_used_gb: float
    gpu_usage: float
    gpu_temp: Optional[float] = None
    health_status: str
    battery_percent: Optional[int] = None
    is_charging: Optional[bool] = None
    is_online: bool = True
    network_type: str
    wifi_ssid: Optional[str] = None
    signal_strength: Optional[int] = None
    ip_address: Optional[str] = None
    ping_ms: Optional[int] = None
    vpn_status: bool = False
    active_window: Optional[str] = None
    last_updated: str

class Device(BaseModel):
    device_id: str
    device_name: str
    nickname: Optional[str] = None
    device_type: str 
    profile: Optional[DeviceSpecs] = None
    status: Optional[DeviceLiveStatus] = None
    trusted: bool = True
    last_seen: datetime = datetime.utcnow()

class DeviceAction(BaseModel):
    action_id: str
    target_device_id: str
    command: str
    payload: Optional[Dict] = {}
    status: str = "pending"
    result: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
