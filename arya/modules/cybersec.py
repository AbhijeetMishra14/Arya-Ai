import subprocess
import threading
import time
import datetime
import ctypes
import os
import re
import psutil
import socket
import concurrent.futures

class CyberSecModule:
    """Defensive Cybersecurity Module: manages Windows Defender, Firewall, and system monitoring."""
    def __init__(self, system_module=None):
        self.system_module = system_module
        self._security_log = []
        self._active_timers = {}

    def monitor_processes(self) -> str:
        """Scans local processes for high resource usage to identify potential anomalies."""
        suspicious = []
        try:
            if self.system_module: self.system_module.set_critical_task("Process Security Monitoring", level=2)
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    name = proc.info.get('name', 'Unknown')
                    cpu = proc.info.get('cpu_percent', 0.0)
                    if cpu is not None and cpu > 70.0:
                        suspicious.append(f"PID {proc.info.get('pid')} ({name}) using {cpu}% CPU")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if self.system_module: self.system_module.clear_critical_task()
            if not suspicious:
                return "Process scan complete. System processes appear nominal."
            return "Process scan complete. High usage anomalies detected:\n" + "\n".join(suspicious)
        except Exception as e:
            if self.system_module: self.system_module.clear_critical_task()
            return f"Failed to monitor system processes: {str(e)}"

    def _scan_port(self, port) -> bool:
        """Helper to scan a single port on localhost."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_local_vulnerabilities(self) -> str:
        """Scans common local ports to ensure no unnecessary services are running and exposed."""
        common_ports = [21, 22, 23, 25, 80, 135, 139, 443, 445, 3389]
        open_ports = []
        try:
            if self.system_module: self.system_module.set_critical_task("Local Port Vulnerability Scanning", level=2)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = executor.map(self._scan_port, common_ports)
            
            for port, is_open in zip(common_ports, list(results)):
                if is_open: open_ports.append(str(port))
            
            if self.system_module: self.system_module.clear_critical_task()
            if not open_ports:
                return "Local port scan complete. No critical exposed ports found on localhost."
            
            report = f"Local port scan complete. Found open ports on localhost: {', '.join(open_ports)}.\n"
            report += "Advice: Review these running services to ensure they aren't externally exposed."
            return report
        except Exception as e:
            if self.system_module: self.system_module.clear_critical_task()
            return f"Failed to scan local vulnerabilities: {str(e)}"

    def _log_security_event(self, action: str, result: str):
        """Internal audit logger for security actions."""
        event = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "result": result
        }
        self._security_log.append(event)
        if self.system_module and hasattr(self.system_module, 'memory') and self.system_module.memory.client:
            try:
                self.system_module.memory.db["security_audit"].insert_one(event)
            except: pass

    def is_admin(self) -> bool:
        """Checks if the process has administrative privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def get_security_status(self) -> str:
        """Retrieves current health and status of Windows Defender and Firewall."""
        if not self.is_admin():
            return "Security Status: Unknown (Admin privileges required for full status check)."
        
        try:
            def_cmd = "powershell -Command \"Get-MpComputerStatus | Select-Object -Property RealTimeProtectionEnabled, AntivirusEnabledByPass, AMServiceEnabled, AntivirusSignatureLastUpdated | ConvertTo-Json\""
            def_res = subprocess.check_output(def_cmd, shell=True).decode().strip()
            fire_cmd = "powershell -Command \"Get-NetFirewallProfile | Select-Object -Property Name, Enabled | ConvertTo-Json\""
            fire_res = subprocess.check_output(fire_cmd, shell=True).decode().strip()
            return f"SYSTEM SECURITY STATUS:\n\nDEFENDER:\n{def_res}\n\nFIREWALL:\n{fire_res}"
        except Exception as e:
            return f"Failed to retrieve security status: {str(e)}"

    def manage_defender(self, action: str, duration_mins: int = 0, confirm: bool = False) -> str:
        """Manages Windows Defender: enable, disable, scan, update."""
        if not self.is_admin():
            return "[PERMISSION] Admin elevation required. Run ARYA as Administrator."

        try:
            if action == "status":
                return self.get_security_status()
            elif action == "disable":
                if not confirm:
                    return "[WARNING] Disabling Real-time Protection reduces your security. Confirm proceed?"
                subprocess.run("powershell -Command \"Set-MpPreference -DisableRealtimeMonitoring $true\"", shell=True, check=True)
                self._log_security_event("Disable Defender", "Success")
                if duration_mins > 0:
                    self._start_restore_timer("defender", duration_mins)
                    return f"Defender DISABLED for {duration_mins} mins. Auto-restore active."
                return "Defender Real-time Protection DISABLED."
            elif action == "enable":
                subprocess.run("powershell -Command \"Set-MpPreference -DisableRealtimeMonitoring $false\"", shell=True, check=True)
                self._log_security_event("Enable Defender", "Success")
                return "Defender Real-time Protection ENABLED."
            elif action == "quick_scan":
                subprocess.Popen("powershell -Command \"Start-MpScan -ScanType QuickScan\"", shell=True)
                return "Defender Quick Scan INITIATED in background."
            elif action == "full_scan":
                subprocess.Popen("powershell -Command \"Start-MpScan -ScanType FullScan\"", shell=True)
                return "Defender Full Scan INITIATED."
            elif action == "update":
                subprocess.run("powershell -Command \"Update-MpSignature\"", shell=True, check=True)
                return "Defender Security Intelligence UPDATED."
        except Exception as e:
            return f"Defender action failed: {str(e)}"

    def manage_firewall(self, action: str, profile: str = "Any", duration_mins: int = 0, confirm: bool = False) -> str:
        """Manages Windows Firewall: enable, disable, reset."""
        if not self.is_admin():
            return "[PERMISSION] Admin elevation required. Please ensure ARYA is running as Administrator."

        # Normalize profile for PowerShell (Any -> All standard profiles)
        ps_profile = profile
        if profile.lower() == "any":
            ps_profile = "Domain,Public,Private"

        try:
            if action == "disable":
                if not confirm:
                    return "[WARNING] Disabling Firewall reduces security. Confirm proceed?"
                
                cmd = f"powershell -ExecutionPolicy Bypass -Command \"Set-NetFirewallProfile -Profile {ps_profile} -Enabled False\""
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return f"Firewall action failed (Windows Error): {result.stderr.strip()}"

                self._log_security_event(f"Disable Firewall ({profile})", "Success")
                if duration_mins > 0:
                    self._start_restore_timer("firewall", duration_mins, profile)
                    return f"Firewall ({profile}) DISABLED for {duration_mins} mins."
                return f"Firewall ({profile}) DISABLED."
                
            elif action == "enable":
                cmd = f"powershell -ExecutionPolicy Bypass -Command \"Set-NetFirewallProfile -Profile {ps_profile} -Enabled True\""
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return f"Firewall action failed (Windows Error): {result.stderr.strip()}"
                    
                self._log_security_event(f"Enable Firewall ({profile})", "Success")
                return f"Firewall ({profile}) ENABLED."
                
            elif action == "reset":
                if not confirm: return "[WARNING] Reset Firewall settings to default? Confirm?"
                result = subprocess.run("netsh advfirewall reset", shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return f"Firewall reset failed: {result.stderr.strip()}"
                return "Firewall RESTORED TO DEFAULTS."
        except Exception as e:
            return f"An internal error occurred: {str(e)}"

    def _start_restore_timer(self, target: str, mins: int, profile: str = "Any"):
        """Timed auto-restoration for security features."""
        def restore():
            if target == "defender": self.manage_defender("enable")
            elif target == "firewall": self.manage_firewall("enable", profile=profile)
            if self.system_module:
                 self.system_module.memory.log_interaction("SYSTEM", f"Security Alert: Auto-restored {target}.")
        timer = threading.Timer(mins * 60, restore)
        timer.daemon = True
        timer.start()

    def get_security_audit_log(self, limit: int = 10) -> str:
        """Retrieves recent security actions taken by ARYA."""
        if not self._security_log: return "No recent security actions."
        summary = "RECENT SECURITY AUDIT LOG:\n"
        for event in self._security_log[-limit:]:
            summary += f"- [{event['timestamp']}] {event['action']}: {event['result']}\n"
        return summary
