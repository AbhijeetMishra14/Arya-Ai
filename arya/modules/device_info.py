import psutil
import platform
import os
import socket
import wmi
import subprocess
from datetime import datetime
import GPUtil
import winreg

class LocalDeviceSystem:
    def __init__(self):
        try: self.w = wmi.WMI()
        except: self.w = None

    def _get_registry_value(self, key_path, value_name):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return str(value).strip()
        except: return None

    def get_static_profile(self):
        mfr = self._get_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemManufacturer") or "Generic"
        model = self._get_registry_value(r"HARDWARE\DESCRIPTION\System\BIOS", "SystemProductName") or "PC"
        
        gpu_name = "Integrated"
        try:
            gpus = GPUtil.getGPUs()
            if gpus: gpu_name = gpus[0].name
        except: pass

        return {
            "model": model,
            "manufacturer": mfr,
            "os_name": platform.system(),
            "os_version": platform.release(),
            "cpu_model": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=True) or 4,
            "cpu_speed": "N/A",
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "gpu_name": gpu_name,
            "gpu_total_vram_gb": 0.0,
            "storage": [{"mount": "C:", "total": 0, "free": 0}],
            "screen_res": "1920x1080",
            "timezone": datetime.now().astimezone().tzname(),
            "first_linked": datetime.utcnow().isoformat()
        }

    def get_live_pulse(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            
            # IP Probe
            ip_addr = "127.0.0.1"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_addr = s.getsockname()[0]
                s.close()
            except: ip_addr = socket.gethostbyname(socket.gethostname())

            gpu_usage = 0.0
            try:
                g = GPUtil.getGPUs()
                if g: gpu_usage = g[0].load * 100
            except: pass

            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else 100
            is_charging = battery.power_plugged if battery else True

            return {
                "cpu_usage": cpu_usage,
                "ram_usage": ram.percent,
                "ram_used_gb": round(ram.used / (1024**3), 2),
                "gpu_usage": round(gpu_usage, 1),
                "battery_percent": battery_percent,
                "is_charging": is_charging,
                "ip_address": ip_addr,
                "health_status": "Healthy" if ram.percent < 90 else "High RAM",
                "is_online": True,
                "network_type": "Wi-Fi" if battery else "Ethernet",
                "wifi_ssid": "Neural Link Active",
                "signal_strength": 100,
                "vpn_status": False,
                "last_updated": datetime.utcnow().isoformat(),
                "storage": [
                    {"mount": p.mountpoint, "free": psutil.disk_usage(p.mountpoint).free}
                    for p in psutil.disk_partitions() if 'fixed' in p.opts or 'rw' in p.opts
                ]
            }
        except: return {}
