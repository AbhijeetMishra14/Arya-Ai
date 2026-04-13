import time
import os
from datetime import datetime

class AutomationEngine:
    def __init__(self, brain, auth_client):
        self.brain = brain
        self.auth = auth_client
        self.rules = []
        self.last_sync = 0

    def sync_rules(self):
        """Fetch active rules from the Neural Grid."""
        if time.time() - self.last_sync > 60: # Sync every minute
            self.rules = self.auth.get_automation_rules()
            self.last_sync = time.time()

    def evaluate_pulse(self, pulse):
        """Check all rules against the current hardware pulse."""
        self.sync_rules()
        
        for rule in self.rules:
            if not rule.get("is_active"): continue
            
            triggered = False
            t_type = rule.get("trigger_type")
            t_cond = rule.get("trigger_condition")
            t_val = rule.get("trigger_value")
            
            try:
                if t_type == "battery":
                    curr = pulse.get("battery_percent", 100)
                    if t_cond == "<" and curr < float(t_val): triggered = True
                    elif t_cond == ">" and curr > float(t_val): triggered = True
                
                elif t_type == "charging":
                    curr = pulse.get("is_charging", True)
                    if t_cond == "becomes_charging" and curr: triggered = True
                    elif t_cond == "becomes_discharging" and not curr: triggered = True
                
                elif t_type == "ram":
                    if pulse.get("ram_usage", 0) > float(t_val): triggered = True
                
                elif t_type == "cpu":
                    if pulse.get("cpu_usage", 0) > float(t_val): triggered = True
                
                elif t_type == "wifi":
                    if t_cond == "matches" and pulse.get("network_type") == t_val: triggered = True
                    elif t_cond == "disconnects" and pulse.get("network_type") == "None": triggered = True

                elif t_type == "storage":
                    # Check if any drive is below threshold GB
                    for drive in pulse.get("storage", []):
                        if (drive.get("free", 100) / (1024**3)) < float(t_val): triggered = True

                if triggered:
                    self._execute_action(rule)
            except: pass

    def _execute_action(self, rule):
        a_type = rule.get("action_type")
        payload = rule.get("action_payload", {})
        
        if a_type == "notification":
            self.brain.system_module.send_notification("ARYA Sentinel", payload.get("text", "Rule triggered."))
        
        elif a_type == "open_app":
            self.brain.system_module.open_application(payload.get("app", "notepad"))
        
        elif a_type == "command":
            import subprocess
            try: subprocess.run(payload.get("cmd", "echo done"), shell=True)
            except: pass

        elif a_type == "lock":
            self.brain.system_module.lock_workstation()

        elif a_type == "volume":
            self.brain.system_module.set_system_volume(payload.get("level", 50))
            
        # Log the automation hit
        print(f"[AUTOMATION]: Rule '{rule.get('name')}' activated.")
