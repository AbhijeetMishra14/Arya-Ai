import time
import logging
import re
from playwright.sync_api import sync_playwright
from arya.core.config import Config

# Configure logging
logging.basicConfig(
    filename='router_control.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RouterModule:
    """Manages Huawei router via admin panel automation."""

    def __init__(self, system_module=None):
        self.url = Config.ROUTER_URL
        self.username = Config.ROUTER_USER
        self.password = Config.ROUTER_PASSWORD
        self.system_module = system_module # Reference for notifications or confirmation states

    def _login(self, page):
        """Final Precision Login logic. Targets specific IDs and verifies fill-state."""
        logging.info("Initiating Final Precision Login.")
        try:
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            page.goto(self.url, timeout=30000, wait_until="networkidle")
            
            # --- 1. PINPOINT USERNAME ---
            user_field = page.locator("#txt_Username, #txt_username, input[id*='User' i]").first
            user_field.wait_for(state="visible", timeout=5000)
            user_field.fill(self.username)
            
            # --- 2. PINPOINT PASSWORD (IMPORTANT: Avoid hidden fields) ---
            # We specifically target txt_Password which is the active login field
            pass_field = page.locator("#txt_Password, #txt_password").first
            if not pass_field.is_visible():
                pass_field = page.locator("input[type='password']:visible").first
                
            pass_field.fill(self.password)
            
            # Double-check fill (some JS clears fields)
            if not pass_field.input_value():
                pass_field.type(self.password, delay=50) # Type manually if fill fails
            
            # --- 3. THE TRIGGER ---
            login_btn = page.locator("#loginbutton, #button_login").first
            login_btn.click(force=True)

            # --- 4. SUCCESS VERIFICATION ---
            try:
                # If we see a dashbaord element, we are in
                page.wait_for_selector("text=WLAN, text=Status, text=Logout", state="visible", timeout=15000)
                logging.info("Access granted. Neural bridge stable.")
                return True
            except:
                # Take one last look
                if any(page.get_by_text(t, exact=False).is_visible() for t in ["Logout", "Home", "Maintain"]):
                    return True
                page.screenshot(path="final_failure_view.png")
                return False

        except Exception as e:
            logging.error(f"Final Precision Login failed: {str(e)}")
            return False

    def get_router_status(self) -> str:
        """Checks WAN status, uptime, and general router health."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                if not self._login(page):
                    return "Neural Error: Failed to authenticate with the router admin panel. Please check credentials."

                # Status info is usually on the home page or 'Status' tab
                # We'll look for common text blocks
                status_text = page.locator("body").inner_text()
                
                # Heuristic extraction
                wan_status = "Connected" if "Connected" in status_text or "Online" in status_text else "Disconnected"
                uptime = "Unknown"
                if "Uptime" in status_text:
                    # Try to extract the line with Uptime
                    lines = status_text.split('\n')
                    for line in lines:
                        if "Uptime" in line:
                            uptime = line.split(":")[-1].strip()
                            break

                browser.close()
                logging.info(f"Status check: WAN={wan_status}, Uptime={uptime}")
                return f"Router Status: WAN is {wan_status}. System Uptime: {uptime}. All neural links are stable."
        except Exception as e:
            logging.error(f"Status check failed: {str(e)}")
            return f"Error checking router status: {str(e)}"

    def reboot_router(self, confirmed: bool = False) -> str:
        """Restarts the router. Requires explicit user confirmation."""
        if not confirmed:
            return "CONFIRMATION_REQUIRED: Rebooting the router will temporarily disconnect all devices. Are you sure you want to proceed?"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                if not self._login(page):
                    return "Authentication failure during reboot sequence."

                # Navigate to reboot page (usually in Management/System/Maintenance)
                # We'll try to find a link or button with 'Reboot' or 'Restart'
                reboot_btn = page.get_by_role("button", name=re.compile("Reboot|Restart", re.I))
                if not reboot_btn.is_visible():
                    # Try searching for a link first
                    page.get_by_text("Management", exact=False).click()
                    page.wait_for_timeout(1000)
                    reboot_btn = page.get_by_role("button", name=re.compile("Reboot|Restart", re.I))

                if reboot_btn.is_visible():
                    reboot_btn.click()
                    # Handle any confirmation alerts
                    page.on("dialog", lambda dialog: dialog.accept())
                    logging.info("Reboot command sent.")
                    browser.close()
                    return "Router restarted successfully. Please wait a few minutes for the network to come back online."
                else:
                    browser.close()
                    return "Could not locate the reboot button in the admin interface."
        except Exception as e:
            logging.error(f"Reboot failed: {str(e)}")
            return f"Reboot sequence interrupted: {str(e)}"

    def get_connected_devices(self) -> str:
        """Retrieves a list of all currently connected devices with IP and Band info."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                if not self._login(page):
                    return "Device scan aborted: Login failed."

                # Huawei HG series logic: Navigate to status or user information
                triggers = ["Status", "User Device", "Connected Devices", "Home"]
                for t in triggers:
                    btn = page.get_by_text(t, exact=False).first
                    if btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(2000)
                        break

                # Extract table information if possible
                # Huawei often uses tables with class 'main_table' or IDs like 'devicelist'
                device_info = []
                
                # Try to scrape table rows
                rows = page.locator("tr").all()
                if len(rows) > 5: # Some rows found
                    for row in rows:
                        txt = row.inner_text().replace('\t', ' ').strip()
                        if any(char.isdigit() for char in txt) and len(txt) > 10:
                            # Filter for strings that look like device info (contain digits, IPs, etc)
                            device_info.append(f"• {txt}")
                else:
                    # Fallback to general text extraction
                    content = page.locator("body").inner_text()
                    lines = content.split('\n')
                    for line in lines:
                        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line) or "Alive" in line:
                            device_info.append(f"• {line.strip()}")

                browser.close()
                
                if not device_info:
                    return "I've successfully logged into the router, but no active device data is currently populated in the status list."

                summary = "\n".join(list(dict.fromkeys(device_info))[:15]) # Limit to top 15 items
                logging.info(f"Device scan successful. Found {len(device_info)} potential entries.")
                return f"Neural Scan Results: I've identified the following active connections:\n{summary}"
        except Exception as e:
            logging.error(f"Device scan failed: {str(e)}")
            return f"Failed to retrieve device list: {str(e)}"

    def change_wifi_settings(self, ssid: str = None, password: str = None, band: str = "2.4G", confirmed: bool = False) -> str:
        """Updates Wi-Fi Name (SSID) or Password for a specific band (2.4G or 5G)."""
        band = band.upper()
        if band not in ["2.4G", "5G"]: band = "2.4G"
        
        if not confirmed:
            action = f"rename the {band} Wi-Fi to '{ssid}'" if ssid and not password else ""
            action += f"change the {band} Wi-Fi password to '{password}'" if password and not ssid else ""
            action = f"change the {band} Wi-Fi name to '{ssid}' and password to '{password}'" if ssid and password else action
            return f"CONFIRMATION_REQUIRED: You are about to {action}. This will disconnect all devices on the {band} band. Proceed?"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                if not self._login(page): return "Wi-Fi update failed: Auth Error."

                # Navigate to WLAN settings
                # Huawei HG series often have separate links for 2.4G and 5G in the sidebar or tabs
                page.get_by_text("WLAN", exact=False).first.click()
                page.wait_for_timeout(2000)

                # Robust band switching logic
                band_triggers = [
                    f"text='{band}'", 
                    f"text='{band} Basic'", 
                    f"span:has-text('{band}')",
                    f"a:has-text('{band}')",
                    f"li:has-text('{band}')"
                ]
                
                band_found = False
                for selector in band_triggers:
                    try:
                        target = page.locator(selector).first
                        if target.is_visible(timeout=1000):
                            target.click()
                            page.wait_for_timeout(1000)
                            band_found = True
                            logging.info(f"Switched to {band} view via: {selector}")
                            break
                    except:
                        continue
                
                if not band_found:
                    logging.warning(f"Could not confirm switch to {band} band. Proceeding with visible page.")

                if ssid:
                    # Common Huawei input IDs include #SSID, #SSIDName, #txtSSID
                    ssid_input = page.locator("input[id*='ssid' i], input[name*='ssid' i], #SSID, #SSIDName").first
                    ssid_input.fill(ssid)
                
                if password:
                    # Common password input IDs include #PSK, #Passphrase, #txtPSK
                    pass_input = page.locator("input[type='password'], input[id*='key' i], input[id*='pwd' i], #PSK, #Passphrase").first
                    pass_input.fill(password)

                # Save changes
                apply_btn = page.get_by_role("button", name=re.compile("Apply|Save|OK", re.I)).first
                apply_btn.click()
                
                logging.info(f"{band} Wi-Fi settings updated. SSID={ssid}, Pass Updated={bool(password)}")
                browser.close()
                return f"{band} Wi-Fi settings updated successfully. Reconnect your devices using the new credentials if necessary."
        except Exception as e:
            logging.error(f"Wi-Fi update failed: {str(e)}")
            return f"{band} Wi-Fi update encounterted an error: {str(e)}"

    def toggle_guest_wifi(self, enable: bool, band: str = "2.4G") -> str:
        """Enables or disables the Guest Wi-Fi network for a specific band."""
        band = band.upper()
        if band not in ["2.4G", "5G"]: band = "2.4G"
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                if not self._login(page): return "Guest Wi-Fi toggle failed: Auth Error."

                # Navigate to Guest Network settings
                page.get_by_text("Guest Network", exact=False).first.click()
                page.wait_for_timeout(2000)

                # Try to target the specific band tab
                target = page.get_by_text(band, exact=False).first
                if target.is_visible():
                    target.click()
                    page.wait_for_timeout(1000)

                # Find checkbox or toggle
                checkbox = page.get_by_role("checkbox").first
                is_checked = checkbox.is_checked()

                if enable and not is_checked:
                    checkbox.check()
                elif not enable and is_checked:
                    checkbox.uncheck()
                
                apply_btn = page.get_by_role("button", name=re.compile("Apply|Save", re.I)).first
                apply_btn.click()

                status = "enabled" if enable else "disabled"
                logging.info(f"{band} Guest Wi-Fi {status}.")
                browser.close()
                return f"{band} Guest Wi-Fi has been successfully {status}."
        except Exception as e:
            logging.error(f"Guest Wi-Fi toggle failed: {str(e)}")
            return f"Failed to toggle {band} Guest Wi-Fi: {str(e)}"
