from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from typing import List, Optional
import os
import shutil
import uuid
import motor.motor_asyncio
from pydantic import BaseModel

from arya_auth import models, db, auth_utils
from arya_auth.db import neural_db, connect_to_mongo, close_mongo_connection

app = FastAPI(title="ARYA Auth & Ecosystem API")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.on_event("startup")
async def startup_db_client():
    print("[SYSTEM]: Initiating Neural Database Connection...")
    try:
        await connect_to_mongo()
        print("[SYSTEM]: Neural Link Established with Atlas.")
    except Exception as e:
        print(f"[CRITICAL ERROR]: Neural Link Failed: {str(e)}")
        # Don't re-raise, let the app start so we can see the logs

# --- AUTH LOGIC ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = auth_utils.decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload.get("sub")

@app.post("/signup")
async def signup(user: models.UserCreate):
    existing = await neural_db.db['users'].find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = auth_utils.get_password_hash(user.password)
    user_in_db = {"email": user.email, "hashed_password": hashed_pw, "created_at": datetime.utcnow()}
    await neural_db.db['users'].insert_one(user_in_db)
    return {"message": "User created successfully"}

@app.post("/login")
async def login(req: LoginRequest):
    if neural_db.db is None: await connect_to_mongo()
    user = await neural_db.db['users'].find_one({"email": req.username})
    if not user or not auth_utils.verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = auth_utils.create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ... (rest of the ecosystem routes remain identical)

@app.post("/devices")
async def register_device(device: models.Device, current_user: str = Depends(get_current_user)):
    device_data = device.dict()
    device_data["user_email"] = current_user
    device_data["last_seen"] = datetime.utcnow()
    existing_device = await neural_db.db['devices'].find_one({"device_id": device.device_id, "user_email": current_user})
    if existing_device and "nickname" in existing_device:
        device_data["nickname"] = existing_device["nickname"]
    await neural_db.db['devices'].update_one({"device_id": device.device_id, "user_email": current_user}, {"$set": device_data}, upsert=True)
    return {"message": "Device synced successfully"}

@app.get("/devices")
async def get_devices(current_user: str = Depends(get_current_user)):
    cursor = neural_db.db['devices'].find({"user_email": current_user})
    devices = await cursor.to_list(length=100)
    for d in devices: d["_id"] = str(d["_id"])
    return devices

@app.patch("/devices/{device_id}")
async def update_device(device_id: str, updates: dict, current_user: str = Depends(get_current_user)):
    await neural_db.db['devices'].update_one({"device_id": device_id, "user_email": current_user}, {"$set": updates})
    return {"message": "Device updated"}

@app.post("/devices/{device_id}/actions")
async def queue_device_action(device_id: str, action: dict, current_user: str = Depends(get_current_user)):
    action_data = {"action_id": str(uuid.uuid4()), "target_device_id": device_id, "user_email": current_user, "command": action.get("command"), "payload": action.get("payload", {}), "status": "pending", "created_at": datetime.utcnow()}
    await neural_db.db['actions'].insert_one(action_data)
    return {"status": "success", "action_id": action_data["action_id"]}

@app.get("/devices/actions/pending")
async def poll_pending_actions(current_user: str = Depends(get_current_user)):
    cursor = neural_db.db['actions'].find({"user_email": current_user, "status": "pending"})
    actions = await cursor.to_list(length=10)
    for a in actions: a["_id"] = str(a["_id"])
    return actions

@app.patch("/devices/actions/{action_id}")
async def update_action_result(action_id: str, update: dict, current_user: str = Depends(get_current_user)):
    await neural_db.db['actions'].update_one({"action_id": action_id, "user_email": current_user}, {"$set": {"status": update.get("status", "completed"), "result": update.get("result"), "completed_at": datetime.utcnow()}})
    return {"status": "updated"}

@app.get("/continuity/clipboard")
async def get_clipboard(current_user: str = Depends(get_current_user)):
    data = await neural_db.db['clipboard'].find_one({"user_email": current_user})
    return {"text": data["text"], "updated_at": data["updated_at"], "source": data["source_device_id"]} if data else {"text": ""}

@app.post("/continuity/clipboard")
async def update_clipboard(payload: dict, current_user: str = Depends(get_current_user)):
    await neural_db.db['clipboard'].update_one({"user_email": current_user}, {"$set": {"text": payload.get("text"), "source_device_id": payload.get("device_id"), "updated_at": datetime.utcnow()}}, upsert=True)
    return {"status": "synced"}

@app.post("/continuity/files/upload")
async def upload_file(target_device_id: str, sender_device_id: str, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    transfer_id = str(uuid.uuid4())
    upload_dir = os.path.join(os.getcwd(), "arya_auth", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{transfer_id}_{file.filename}")
    with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    await neural_db.db['transfers'].insert_one({"transfer_id": transfer_id, "user_email": current_user, "sender_device_id": sender_device_id, "receiver_device_id": target_device_id, "file_name": file.filename, "file_path": file_path, "status": "ready", "created_at": datetime.utcnow()})
    return {"status": "ready", "transfer_id": transfer_id}

@app.get("/continuity/files/pending")
async def get_pending_transfers(current_user: str = Depends(get_current_user)):
    cursor = neural_db.db['transfers'].find({"user_email": current_user, "status": "ready"})
    transfers = await cursor.to_list(length=10)
    for t in transfers: t["_id"] = str(t["_id"])
    return transfers

@app.get("/continuity/files/download/{transfer_id}")
async def download_file(transfer_id: str, current_user: str = Depends(get_current_user)):
    transfer = await neural_db.db['transfers'].find_one({"transfer_id": transfer_id, "user_email": current_user})
    return FileResponse(transfer["file_path"], filename=transfer["file_name"]) if transfer else HTTPException(404, "Not found")

@app.get("/devices/actions/{action_id}")
async def get_action_status(action_id: str, current_user: str = Depends(get_current_user)):
    action = await neural_db.db['actions'].find_one({"action_id": action_id})
    if not action: raise HTTPException(status_code=404, detail="Action not found")
    return action

@app.get("/devices/{device_id}/history")
async def get_device_history(device_id: str, current_user: str = Depends(get_current_user)):
    cursor = neural_db.db['actions'].find({"target_device_id": device_id}).sort("created_at", -1).limit(50)
    return await cursor.to_list(length=50)

@app.delete("/continuity/files/{transfer_id}")
async def clear_transfer(transfer_id: str, current_user: str = Depends(get_current_user)):
    await neural_db.db['transfers'].delete_one({"transfer_id": transfer_id})
    return {"status": "cleared"}

@app.delete("/devices/all")
async def purge_all_devices(current_user: str = Depends(get_current_user)):
    await neural_db.db['devices'].delete_many({"user_email": current_user})
    return {"status": "success", "message": "All ecosystem nodes cleared. Please relink devices."}

# --- AUTOMATION ENGINE ROUTES ---
@app.get("/automations")
async def get_automations(current_user: str = Depends(get_current_user)):
    cursor = neural_db.db['automations'].find({"user_email": current_user})
    return await cursor.to_list(length=100)

@app.post("/automations")
async def create_automation(rule: models.AutomationRule, current_user: str = Depends(get_current_user)):
    rule_data = rule.dict()
    rule_data["user_email"] = current_user
    await neural_db.db['automations'].insert_one(rule_data)
    return {"status": "rule_created", "rule_id": rule.rule_id}

@app.delete("/automations/{rule_id}")
async def delete_automation(rule_id: str, current_user: str = Depends(get_current_user)):
    await neural_db.db['automations'].delete_one({"rule_id": rule_id, "user_email": current_user})
    return {"status": "rule_deleted"}
