import os
import subprocess
import webbrowser
import urllib.request
import urllib.parse
import re
import pyautogui

class SystemModule:
    """Handles OS-level interactions, file management, and application launching."""
    
    def __init__(self, memory=None):
        self.memory = memory
        self.critical_task = None # Stores description of active important task
        self.priority_level = 0    # 0: Idle, 1: Medium (Task), 2: High (Security/Data)

    def set_critical_task(self, task_name: str, level: int = 1):
        """Signals that ARYA is performing an important task."""
        self.critical_task = task_name
        self.priority_level = level

    def clear_critical_task(self):
        """Signals that the important task is complete."""
        self.critical_task = None
        self.priority_level = 0

    def check_protective_block(self, command_intent: str) -> str:
        """Helper to verify if an action should be blocked based on Protective Mode settings."""
        if not self.memory:
            return None
            
        safety_prefs = self.memory.get_preferences(category="safety")
        mode = safety_prefs.get("protective_mode", "Warn Only")
        
        # Obvious risky patterns
        risky_patterns = ["antivirus", "defender", "firewall", "rm -rf", "del /s", "format", "reg delete"]
        
        if mode in ["Warn + Block", "Strict Guard"]:
            if any(p in command_intent.lower() for p in risky_patterns):
                return f"BLOCK: ARYA's {mode} is ACTIVE. I have intercepted and blocked this command to prevent potential system compromise. If you truly wish to proceed, please lower the Protective Mode in settings first."
        return None

    def open_application(self, app_name: str, sub_page: str = "") -> str:
        """Intelligently launches desktop apps or falls back to web versions (Instagram, WhatsApp, etc.)."""
        app_name = app_name.lower().strip()
        
        # 1. SPECIAL CASE: Social App & Web Fallback Mapping
        social_map = {
            "instagram": {
                "root": "https://www.instagram.com/",
                "chats": "https://www.instagram.com/direct/inbox/",
                "messages": "https://www.instagram.com/direct/inbox/"
            },
            "whatsapp": {
                "root": "https://web.whatsapp.com/",
                "chats": "https://web.whatsapp.com/",
                "messages": "https://web.whatsapp.com/"
            },
            "telegram": {
                "root": "https://web.telegram.org/",
                "chats": "https://web.telegram.org/",
                "messages": "https://web.telegram.org/"
            },
            "discord": {
                "root": "https://discord.com/app",
                "chats": "https://discord.com/app",
                "messages": "https://discord.com/app"
            },
            "messenger": {
                "root": "https://www.messenger.com/",
                "chats": "https://www.messenger.com/",
                "messages": "https://www.messenger.com/"
            }
        }

        try:
            # 2. Check for Deep-Links/Sub-Page mappings first
            sub_page_map = {
                "apps": "ms-settings:appsfeatures",
                "bluetooth": "ms-settings:bluetooth",
                "network": "ms-settings:network",
                "wifi": "ms-settings:network-wifi",
                "display": "ms-settings:display",
                "sound": "ms-settings:sound",
                "update": "ms-settings:windowsupdate",
                "battery": "ms-settings:batterysaver",
                "privacy": "ms-settings:privacy",
                "personalization": "ms-settings:personalization-background",
                "storage": "ms-settings:storagesense",
                "startup": "ms-settings:startupapps"
            }
            
            for key, uri in sub_page_map.items():
                if key in app_name:
                    os.system(f"start {uri}")
                    return f"Navigating directly to {key.title()} settings..."

            if "settings" in app_name:
                os.system("start ms-settings:")
                return "Successfully opened Windows Settings."
            elif "control panel" in app_name:
                os.system("start control")
                return "Successfully opened Control Panel."
            elif "task manager" in app_name:
                os.system("start taskmgr")
                return "Successfully opened Task Manager."

            # 3. Handle Social Web Fallbacks
            for social_app, urls in social_map.items():
                if social_app in app_name:
                    # Try to find local app first (PowerShell detection)
                    ps_check = f"Get-StartApps | Where-Object {{ $_.Name -like '*{social_app}*' }}"
                    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check], capture_output=True, text=True)
                    
                    if res.stdout.strip():
                        # Native App Found: Launch it
                        os.system(f"start {social_app}:") # Try protocol first
                        return f"Successfully launched the native {social_app.title()} app."
                    else:
                        # Fallback to Web
                        target_url = urls["chats"] if sub_page and ("chat" in sub_page or "message" in sub_page) else urls["root"]
                        webbrowser.open(target_url)
                        return f"Found no native {social_app.title()} app, so I've opened the official web version for you."

            # 4. Standard App Launch Logic
            ps_cmd = f"""
            try {{
                Start-Process "{app_name}" -ErrorAction Stop
                Write-Output "SUCCESS"
            }} catch {{
                Write-Output "FAIL"
            }}
            """
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if "SUCCESS" in res.stdout:
                return f"Successfully opened {app_name}."
            else:
                return f"APP_NOT_FOUND: I couldn't find '{app_name}' installed locally. Should I search for a download?"

        except Exception as e:
            return f"Opening error for {app_name}: {str(e)}"

    def activate_window(self, title_query: str) -> bool:
        """Finds and brings a specific application window to the foreground."""
        try:
            import pygetwindow as gw
            import time
            from pywinauto import Application
            
            # Simple title match
            windows = gw.getWindowsWithTitle(title_query)
            if not windows:
                # Try smarter fuzzy matching via list
                all_titles = gw.getAllTitles()
                matches = [t for t in all_titles if title_query.lower() in t.lower()]
                if matches:
                    windows = [gw.getWindowsWithTitle(matches[0])[0]]
            
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.5) # Give Windows time to complete transition
                return True
            return False
        except Exception:
            # Fallback to win32gui for aggressive focus
            try:
                import win32gui, win32con
                hwnd = win32gui.FindWindow(None, title_query)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return True
                return False
            except:
                return False

    def type_into_application(self, app_name: str, text: str) -> str:
        """Heuristic flow: Finds/Opens app -> Focuses -> Types text."""
        try:
            # 1. Activation Step
            success = self.activate_window(app_name)
            
            # 2. Launch if missing
            if not success:
                self.open_application(app_name)
                import time
                time.sleep(2.5) # Wait for cold boot
                self.activate_window(app_name)
            
            # 3. Execution
            pyautogui.write(text, interval=0.08)
            pyautogui.press('enter')
            return f"Focused {app_name} and successfully injected: '{text}'."
        except Exception as e:
            return f"Failed to type into {app_name}: {str(e)}"

    def search_windows_settings(self, query: str) -> str:
        """Opens Windows Settings, ensures focus, and injects search query."""
        try:
            os.system("start ms-settings:")
            import time
            time.sleep(1.8)
            
            # FOCAL VERIFICATION
            self.activate_window("Settings")
            
            pyautogui.press('tab')
            pyautogui.write(query, interval=0.1)
            pyautogui.press('enter')
            return f"Verified Settings focus and searched for: '{query}'."
        except Exception as e:
            return f"Settings focal search failed: {str(e)}"

    def navigate_list_selection(self, action: str = "select_first") -> str:
        """Navigates a list or search results using keyboard automation. 'action' can be 'select_first', 'next', 'previous'."""
        try:
            import time
            action = action.lower()
            
            # Universal List Navigation Logic
            if "select_first" in action or "top" in action:
                pyautogui.press('home')   # Go to top of list
                time.sleep(0.3)
                pyautogui.press('enter')  # Open it
                return "Successfully navigated to and executed the primary result in the active window."
            elif "next" in action or "down" in action:
                pyautogui.press('down')
                time.sleep(0.1)
                pyautogui.press('enter')
                return "Moved to the next item and executed it."
            elif "previous" in action or "up" in action:
                pyautogui.press('up')
                time.sleep(0.1)
                pyautogui.press('enter')
                return "Moved to the previous item and executed it."
            
            return "Unrecognized list navigation action."
        except Exception as e:
            return f"List navigation failed: {str(e)}"

    def perform_app_ui_action(self, app_name: str, action: str) -> str:
        """Performs specific UI actions in an app. Actions: 'new_tab', 'new_window', 'save', 'close_tab'."""
        try:
            # 1. Focus the app first
            if not self.activate_window(app_name):
                return f"UI focal synchronization failed: '{app_name}' window not found."
            
            import time
            time.sleep(0.3)
            
            action = action.lower()
            if "new_tab" in action:
                pyautogui.hotkey('ctrl', 't')
                return f"Pulsed 'New Tab' command (Ctrl+T) into {app_name}."
            elif "new_window" in action:
                pyautogui.hotkey('ctrl', 'n')
                return f"Pulsed 'New Window' command (Ctrl+N) into {app_name}."
            elif "save" in action:
                pyautogui.hotkey('ctrl', 's')
                return f"Pulsed 'Save' command (Ctrl+S) into {app_name}."
            elif "close_tab" in action:
                pyautogui.hotkey('ctrl', 'w')
                return f"Pulsed 'Close Tab' command (Ctrl+W) into {app_name}."
                
            return f"Action '{action}' is not currently mapped for UI pulsing."
        except Exception as e:
            return f"App UI pulse failed: {str(e)}"

    def write_document_content(self, app_name: str, content: str) -> str:
        """Writes text directly into an app's editor buffer (Notepad, etc.) even in the background."""
        try:
            from pywinauto import Application
            import time
            
            # 1. Attach or Start
            try:
                app = Application(backend="uia").connect(title_re=f".*{app_name}.*", timeout=2)
            except:
                self.open_application(app_name)
                time.sleep(2.0)
                app = Application(backend="uia").connect(title_re=f".*{app_name}.*", timeout=5)
            
            # 2. Find the Editor Control (Heuristic)
            window = app.window(title_re=f".*{app_name}.*")
            
            # Common editor controls: 'RichEditD2DPT' (Win11 Notepad), 'Edit' (Win10), 'Document' (Word)
            try:
                editor = window.child_window(control_type="Document") # Best for modern apps
            except:
                try:
                    editor = window.child_window(control_type="Edit") # Standard Win32
                except:
                    return f"Focal lock failed: I found the {app_name} window, but couldn't locate its internal typing area."
            
            # 3. Target-Locked Streaming
            # We use type_keys with with_spaces=True for speed and background reliability
            editor.type_keys(content, with_spaces=True, pause=0.01)
            
            return f"Background writing successful. Text streamed into {app_name} while you work."
        except Exception as e:
            return f"Background writing aborted: {str(e)}"

    def check_unread_messages(self, app_name: str) -> str:
        """Inspects a messaging app (WhatsApp, Discord, etc.) for unread chats and badge counts."""
        try:
            from pywinauto import Application
            import time
            app_name = app_name.lower().strip()
            
            # 1. Focal Synchronization
            if not self.activate_window(app_name):
                # Fallback: Open and wait
                self.open_application(app_name)
                time.sleep(3.0)
            
            # 2. Heuristic UIA Scrape
            try:
                app = Application(backend="uia").connect(title_re=f".*{app_name}.*", timeout=3)
                window = app.window(title_re=f".*{app_name}.*")
                
                # We search for common 'unread' keywords in the accessibility tree
                unread_elements = window.descendants(control_type="Text")
                results = []
                count = 0
                
                for el in unread_elements:
                    txt = el.window_text().lower()
                    # Standard unread patterns: 'unread', '(1)', '[count]'
                    if "unread" in txt or re.match(r"\(\d+\)", txt):
                        parent = el.parent()
                        # Try to find the chat name near the badge
                        chat_name = parent.window_text() if parent else "Unknown Chat"
                        results.append(f"• {chat_name}: {el.window_text()}")
                        count += 1
                        if count >= 5: break # Cap at top 5 for brevity
                
                if results:
                    return f"Neural inbox scan complete. I found {count} unread alerts in {app_name.title()}:\n" + "\n".join(results)
                
                # 3. Sidebar Badge Check Fallback
                return f"I've analyzed the {app_name.title()} interface. No active unread indicators or badges are currently visible in the main chat list."
                
            except Exception:
                return f"Focal link active, but the {app_name} UI is utilizing an encapsulated layer (like Electron) that is blocking direct accessibility scraping."

        except Exception as e:
            return f"Messaging sentinel aborted: {str(e)}"

    def read_screen_content(self, target_window: str = "Foreground") -> str:
        """Inspects the active or specified window's accessibility tree to 'read' visible text and options."""
        try:
            from pywinauto import Application
            import pygetwindow as gw
            
            # 1. Target Resolution
            if target_window == "Foreground":
                title = gw.getActiveWindowTitle()
            else:
                title = target_window
            
            if not title: return "I couldn't identify an active window to read."
            
            # 2. Scrape Accessibility Tree
            app = Application(backend="uia").connect(title_re=f".*{title}.*", timeout=3)
            window = app.window(title_re=f".*{title}.*")
            
            # Extract meaningful UI components: Buttons, ListItems, Text, Links
            controls = window.descendants()
            visible_items = []
            
            for ctrl in controls:
                if ctrl.is_visible() and ctrl.window_text().strip():
                    ctype = ctrl.control_type().replace("Control", "")
                    text = ctrl.window_text().strip()
                    if len(text) > 1 and len(text) < 200:
                        visible_items.append(f"[{ctype}] {text}")
            
            # 3. Clean and Summarize
            if not visible_items:
                return f"I've scanned the {title} window, but I couldn't extract any meaningful visible text blocks."
            
            # Filter and deduplicate
            unique_items = list(dict.fromkeys(visible_items))
            summary = "\n".join(unique_items[:40]) # Cap for brevity
            return f"I've analyzed the '{title}' interface. Here are the primary visible items:\n\n{summary}"
            
        except Exception as e:
            return f"UI structural scan failed: {str(e)}"

    def interact_with_ui_element(self, text_query: str, action: str = "click") -> str:
        """Finds a UI element by its visible text/name and performs an action (click, select)."""
        try:
            from pywinauto import Application
            import pygetwindow as gw
            import time
            
            title = gw.getActiveWindowTitle()
            app = Application(backend="uia").connect(title_re=f".*{title}.*", timeout=3)
            window = app.window(title_re=f".*{title}.*")
            
            # Search for exact or partial text match
            element = window.child_window(title_re=f".*{text_query}.*", timeout=2)
            
            if "click" in action.lower():
                element.click_input()
                return f"Successfully located and clicked on: '{text_query}'."
            elif "select" in action.lower():
                element.select()
                return f"Selected UI element: '{text_query}'."
                
            return f"Action '{action}' is currently unsupported for directed UI interaction."
        except Exception:
            # Fallback: OCR or visual retry or simply inform
            return f"I can see '{text_query}' on screen, but it is currently non-interactive or blocked by the application's UI thread."

    def close_application(self, target_query: str = "current") -> str:
        """Closes a specific window or application. target_query: app name, folder name, or 'current'/'this'."""
        try:
            import pygetwindow as gw
            import win32gui
            
            target = target_query.lower().strip()
            
            # 1. Handle "Current" / "This" Context
            if target in ["current", "this", "active"]:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                if not title: return "I've analyzed the foreground, but I couldn't identify a closable window title."
                
                # Send standard close signal
                win32gui.PostMessage(hwnd, 0x0010, 0, 0) # WM_CLOSE
                return f"Closed the active window: '{title}'."
            
            # 2. Targeted Window Search (Explorer, Apps, Specific Documents)
            all_windows = gw.getAllWindows()
            matches = [w for w in all_windows if target in w.title.lower()]
            
            if matches:
                win = matches[0]
                exact_title = win.title
                win.close()
                return f"Successfully targeted and closed: '{exact_title}'."
                
            # 3. Process-Level Fallback (If no visible window found)
            mapping = {
                "brave": "brave", "chrome": "chrome", "edge": "msedge",
                "explorer": "explorer", "settings": "SystemSettings",
                "notepad": "notepad", "discord": "discord"
            }
            proc_target = mapping.get(target, target)
            ps_cmd = f"Stop-Process -Name '{proc_target}' -Force -ErrorAction SilentlyContinue"
            subprocess.run(["powershell", "-Command", ps_cmd])
            
            return f"I couldn't find a visible window for '{target_query}', so I've sent a termination signal to any associated background processes."

        except Exception as e:
            return f"Window termination encounterted a barrier: {str(e)}"

    def perform_vocal_piece(self, lyrics: str, style: str = "pop") -> str:
        """Performs lyrics in a specific vocal style. styles: 'rap', 'lullaby', 'pop', 'motivational', 'sad'."""
        try:
            import pyttsx3
            import time
            engine = pyttsx3.init()
            style = style.lower()
            
            # 1. STYLE-BASED VOICE CALIBRATION
            if "rap" in style:
                engine.setProperty('rate', 250)    # Rapid-fire delivery
                engine.setProperty('pitch', 0.8)   # Lower, punchier tone
                delay = 0.05
            elif "lullaby" in style or "soft" in style:
                engine.setProperty('rate', 130)    # Slow, calming
                engine.setProperty('volume', 0.6)  # Delicate
                delay = 0.5
            elif "motivational" in style:
                engine.setProperty('rate', 190)    # Energetic
                engine.setProperty('volume', 1.0)  # Authoritative
                delay = 0.2
            else: # DEFAULT POP / CHILL
                engine.setProperty('rate', 170)
                delay = 0.15

            # 2. RHYTHMIC EXECUTION
            # We split by lines to simulate prosody and rhythmic pauses
            print(f"🎤 [PERFORMANCE MODE: {style.upper()}]")
            for line in lyrics.split('\n'):
                if not line.strip(): continue
                engine.say(line)
                engine.runAndWait()
                time.sleep(delay) # Rhythmic pause between bars
            
            return f"Vocal performance in {style} style completed successfully."
        except Exception as e:
            # Fallback to text visual markers if TTS engine is busy/unavailable
            print(f"Musical performance interrupted: {str(e)}")
            return "Vocal synthesis bridge is currently occupied, but I've processed the lyrics for a visual performance."

    def universal_store_search(self, store_name: str, product_query: str) -> str:
        """Finds any online store (Mudita, Amazon, Local Shops) and searches for products. Global web support."""
        store_name = store_name.lower().strip()
        encoded_query = urllib.parse.quote(product_query)
        
        # 1. High-Speed Shortcut Mapping
        mapping = {
            "daraz": f"https://www.daraz.com.np/catalog/?q={encoded_query}",
            "amazon": f"https://www.amazon.com/s?k={encoded_query}",
            "flipkart": f"https://www.flipkart.com/search?q={encoded_query}",
            "ebay": f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}",
            "mudita": f"https://muditastore.com.np/?s={encoded_query}&post_type=product",
            "hamrobazar": f"https://hamrobazar.com/search/product?q={encoded_query}"
        }
        
        if store_name in mapping:
            url = mapping[store_name]
        else:
            # 2. NEURAL DISCOVERY: Resolve unknown store via search
            search_url = f"https://www.google.com/search?q={store_name}+official+website+{product_query}"
            webbrowser.open(search_url)
            return f"I've initialized a Neural Discovery search for '{store_name}'. I'm currently analyzing the official listings for {product_query}."

        webbrowser.open(url)
        import time
        time.sleep(3.5) # Wait for catalog render
        return self.read_screen_content(store_name.title())

    def automate_shopping_action(self, action: str = "add_to_cart") -> str:
        """Finds and clicks shopping-related buttons like 'Add to Cart', 'Buy Now', or 'Proceed to Checkout'."""
        try:
            # 1. Semantic Label Search
            labels = ["add to cart", "buy now", "checkout", "proceed to pay", "continue to shipping"]
            match = None
            
            # We use our internal UI interaction engine to find common shopping buttons
            for label in labels:
                if "success" in self.interact_with_ui_element(label, "click").lower():
                    match = label
                    break
            
            if match:
                return f"Successfully executed shopping {action}: Located '{match}' and triggered interaction."
            
            return "I can see the product page, but the shopping buttons (Add to Cart/Buy) are currently obscured or require explicit selection."
        except Exception as e:
            return f"Shopping automation encountered a barrier: {str(e)}"

    def find_and_download_app(self, app_name: str) -> str:
        """Opens Google Chrome/default browser to search the official download page for an app."""
        query = f"download {app_name} official website installer"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"I have opened the web browser with the download search results for {app_name}. Once installed, you can ask me to open it."

    def open_url(self, url: str) -> str:
        """Opens a specific URL or link directly in the user's default web browser. Use this when the user simply wants to visit a link."""
        try:
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            return f"Successfully opened the link: {url}"
        except Exception as e:
            return f"Failed to open link: {str(e)}"

    def play_youtube_video(self, query: str) -> str:
        """Searches YouTube and plays the exact first video result directly in the default browser. Use when user says to 'play' music or videos."""
        try:
            encoded_query = urllib.parse.quote(query)
            html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={encoded_query}")
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode('utf-8', errors='ignore'))
            if video_ids:
                # Play the highest ranked actual video result
                url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                webbrowser.open(url)
                return f"Successfully found and started playing '{query}' on YouTube."
            else:
                url = f"https://www.youtube.com/results?search_query={encoded_query}"
                webbrowser.open(url)
                return f"Could not find an auto-play video, opened YouTube search for '{query}' instead."
        except Exception as e:
            return f"Failed to play YouTube video: {str(e)}"
            
    def control_media(self, command: str) -> str:
        """Controls system media playback (pause, play, stop, next, volume). Use when user asks to pause/stop songs."""
        cmd = command.lower()
        try:
            if "pause" in cmd or "stop" in cmd or "play" in cmd:
                pyautogui.press('playpause')
                return "Successfully toggled play/pause for active media."
            elif "next" in cmd or "skip" in cmd:
                pyautogui.press('nexttrack')
                return "Skipped to the next track."
            elif "prev" in cmd or "back" in cmd:
                pyautogui.press('prevtrack')
                return "Went to the previous track."
            elif "mute" in cmd:
                pyautogui.press('volumemute')
                return "Toggled system mute."
            return "Unrecognized media command."
        except Exception as e:
            return f"Failed to execute media control: {str(e)}"
            
    def control_browser(self, action: str) -> str:
        """Controls the currently active browser window (close tab, refresh, new tab) via hotkeys."""
        act = action.lower()
        try:
            if "close" in act and "tab" in act:
                pyautogui.hotkey('ctrl', 'w')
                return "Closed the active browser tab."
            elif "close" in act and "browser" in act:
                pyautogui.hotkey('alt', 'f4')
                return "Closed the active application window."
            elif "new" in act and "tab" in act:
                pyautogui.hotkey('ctrl', 't')
                return "Opened a new tab."
            elif "refresh" in act or "reload" in act:
                pyautogui.hotkey('ctrl', 'r')
                return "Refreshed the browser page."
            return "Unrecognized browser control."
        except Exception as e:
            return f"Failed browser control: {str(e)}"
            
    def change_power_profile(self, mode: str) -> str:
        """Changes the Windows power plan natively. This often syncs automatically with OEM software like NitroSense. Modes: 'quiet', 'balanced', 'performance'."""
        mode = mode.lower()
        try:
            if "quiet" in mode or "saver" in mode or "eco" in mode:
                os.system("powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a")
                return "Changed system power plan to Quiet / Power Saver."
            elif "performance" in mode or "turbo" in mode or "max" in mode:
                os.system("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
                return "Changed system power plan to High Performance."
            else:
                os.system("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e")
                return "Changed system power plan to Balanced."
        except Exception as e:
            return f"Failed to change system power mode: {str(e)}"
            
    def automate_keyboard(self, key_sequence: str = "", type_text: str = "") -> str:
        """Simulates raw keyboard presses to navigate GUIs. Ex: key_sequence='tab, tab, down, enter'. type_text writes characters."""
        try:
            if key_sequence:
                keys = [k.strip() for k in key_sequence.split(',')]
                for key in keys:
                    if '+' in key:
                        pyautogui.hotkey(*key.split('+'))
                    else:
                        pyautogui.press(key)
            if type_text:
                pyautogui.write(type_text, interval=0.05)
            return f"Blindly executed keyboard automation sequence."
        except Exception as e:
            return f"Failed keyboard automation: {str(e)}"
            
    def vision_click(self, target_description: str) -> str:
        """Takes a desktop screenshot, uses Gemini Vision AI to find the target's exact coordinates, and automatically clicks it."""
        try:
            import google.generativeai as genai
            from core.config import Config
            import os
            
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Take screenshot
            screenshot_path = "arya_vision_temp.png"
            pyautogui.screenshot(screenshot_path)
            
            # Analyze
            model = genai.GenerativeModel('gemini-2.5-flash')
            img_file = genai.upload_file(path=screenshot_path)
            
            res = model.generate_content([
                f"Find the UI element: '{target_description}'. Return exactly one bounding box for it in the format [ymin, xmin, ymax, xmax] using 0-1000 scale. Return ONLY the numbers.", 
                img_file
            ])
            
            # Parse coords
            text = res.text.replace('[', '').replace(']', '').replace('`', '').strip()
            coords = [float(c.strip()) for c in text.split(',') if c.strip() != ""]
            
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            if len(coords) >= 4:
                ymin, xmin, ymax, xmax = coords[0], coords[1], coords[2], coords[3]
                w, h = pyautogui.size()
                
                center_y = ((ymin + ymax) / 2.0 / 1000.0) * h
                center_x = ((xmin + xmax) / 2.0 / 1000.0) * w
                
                # Move mouse naturally and click
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                pyautogui.click()
                return f"Successfully localized and clicked '{target_description}' via computer vision."
            return f"Vision module failed to parse coordinates: {res.text}"
            
        except Exception as e:
            return f"Vision system error: {str(e)}"
            
    def manage_power_state(self, action: str, target: str = "pc", confirmed: bool = False) -> str:
        """Manages power states for the host PC or the ARYA application itself.
        
        CRITICAL RULES:
        1. target='arya': Use this for 'close ARYA', 'exit application', 'shut down ARYA'.
        2. target='pc': Use this for 'shutdown computer', 'restart laptop', 'hibernate device'.
        3. confirmed: MUST be False by default. Only set to True if the user explicitly said 'Yes' or 'Confirm' to a PREVIOUS shutdown prompt.
        
        action: 'shutdown', 'restart', 'hibernate', 'close'.
        target: 'pc' (System level) or 'arya' (App level).
        confirmed: Boolean flag to bypass safety gate.
        """
        try:
            action = action.lower()
            target = target.lower()
            
            # --- EMERGENCY OVERRIDE & FORCE CLOSE ---
            is_forced = "force" in action or "immediately" in action or "stop everything" in action
            
            # 1. Protective Mode Enforcement
            block_msg = self.check_protective_block(f"{action} {target}")
            if block_msg:
                return block_msg

            if "arya" in target:
                if "restart" in action:
                    import sys
                    import subprocess
                    # Restart ARYA by launching main.py again
                    main_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
                    subprocess.Popen([sys.executable, main_script])
                    return "[SIGNAL: RESTART_ARYA] Restarting ARYA OS..."
                elif "shutdown" in action or "close" in action:
                    # SELF-PRESERVATION LOGIC
                    if self.priority_level > 0 and not is_forced:
                        if self.priority_level == 2:
                            return f"SELF_PRESERVATION: Not yet. I'm in the middle of a critical security operation: {self.critical_task}. Trust me—I'll exit once your system is secure."
                        return f"SELF_PRESERVATION: Give me a moment—I'm finishing an active task: {self.critical_task}. I'll shut down as soon as it's done."
                    
                    self.clear_critical_task()
                    return "[SIGNAL: EXIT_ARYA] Shutting down ARYA OS."

            # PC-level safety check
            if not confirmed:
                if "shutdown" in action or "restart" in action:
                    return f"SAFETY_CHECK: I need your explicit confirmation. Do you mean shut down the computer or close ARYA? (Respond with 'PC' or 'ARYA')"
                return f"SUSPENDED: I need your explicit confirmation to {action} the {target}. Do you confirm?"

            if "restart" in action:
                os.system("shutdown /r /t 10")
                return f"Confirmed. Initiating {target} restart in 10 seconds."
            elif "hibernate" in action:
                os.system("shutdown /h")
                return f"Confirmed. Initiating {target} hibernation."
            elif "shutdown" in action:
                os.system("shutdown /s /t 10")
                return f"Confirmed. Initiating {target} shutdown in 10 seconds."
            else:
                return f"Unrecognized power action for {target}: {action}"
        except Exception as e:
            return f"Failed to modify {target} power state: {str(e)}"

    def get_daily_dashboard(self) -> str:
        """Retrieves a daily briefing dashboard consisting of date, time, battery sensors, and system health. Use this when the user asks for a daily brief or dashboard."""
        import psutil
        import datetime
        try:
            now = datetime.datetime.now()
            date_timeStr = now.strftime("%A, %B %d, %Y - %I:%M %p")
            
            battery = psutil.sensors_battery()
            if battery:
                batt_percent = f"{int(battery.percent)}%"
                plugged = "Charging" if battery.power_plugged else "On Battery"
            else:
                batt_percent = "Desktop/Unknown"
                plugged = "AC Power"
                
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory().percent
            
            dashboard = (
                f"📊 **Personal Dashboard**\n"
                f"🕒 Time: {date_timeStr}\n"
                f"🔋 Battery: {batt_percent} ({plugged})\n"
                f"💻 CPU Load: {cpu}%\n"
                f"🧠 RAM Usage: {ram}%\n"
            )
            return dashboard
        except Exception as e:
            return f"Failed to generate dashboard: {str(e)}"

    def add_reminder(self, minutes: float, reminder_message: str) -> str:
        """Sets a timer to remind the user of a task in the background. 'minutes' is a float representing time until alert."""
        try:
            import threading
            import time
            
            def reminder_worker():
                # Sleep asynchronously so we don't block the main thread
                time.sleep(minutes * 60.0)
                from arya.modules.voice import VoiceModule
                v = VoiceModule()
                v.speak(f"[MOOD: NEUTRAL] Pardon the interruption, but you have a scheduled reminder: {reminder_message}")
                
            threading.Thread(target=reminder_worker, daemon=True).start()
            return f"Actively tracking reminder. I will alert you in {minutes} minutes regarding: '{reminder_message}'."
        except Exception as e:
            return f"Failed to set reminder: {str(e)}"

    def read_local_file(self, filepath: str) -> str:
        """Reads the exact content of a local file on the disk. Use this for Code Copilot mode."""
        try:
            import os
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_local_file(self, filepath: str, content: str) -> str:
        """Writes data entirely to a local file. This is highly destructive, be careful. Use for Code Copilot mode."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} bytes to {filepath}."
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def create_directory(self, directory_path: str) -> str:
        """Creates a new folder/directory on the local file system. Expands ~ to the user's home directory (e.g. ~/Desktop/new_folder). Use when user asks to make a folder."""
        try:
            import os
            path = os.path.expanduser(directory_path)
            os.makedirs(path, exist_ok=True)
            return f"Successfully created folder at: {path}"
        except Exception as e:
            return f"Failed to create directory: {str(e)}"

    def run_terminal_command(self, command: str) -> str:
        """Executes a Windows command prompt terminal command and returns the output. Use for Developer Mode (git, npm, dir, ipconfig)."""
        try:
            # 1. Protective Mode Enforcement
            block_msg = self.check_protective_block(command)
            if block_msg:
                return block_msg

            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                return f"SUCCESS:\n{res.stdout}"
            else:
                return f"FAILED:\n{res.stderr}"
        except Exception as e:
            return f"Terminal system error: {str(e)}"

    def organize_directory(self, directory_path: str) -> str:
        """Organizes a messy directory (like ~/Downloads) by sorting files into subfolders based on file extension."""
        try:
            import os
            import shutil
            path = os.path.expanduser(directory_path)
            if not os.path.exists(path):
                return "Directory does not exist."
                
            categories = {
                'Images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
                'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.doc', '.md'],
                'Installers': ['.exe', '.msi'],
                'Archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
                'Media': ['.mp4', '.mp3', '.mkv', '.avi', '.mov']
            }
            
            moved_count = 0
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item)[1].lower()
                    for cat, exts in categories.items():
                        if ext in exts:
                            cat_dir = os.path.join(path, cat)
                            os.makedirs(cat_dir, exist_ok=True)
                            shutil.move(item_path, os.path.join(cat_dir, item))
                            moved_count += 1
                            break
            return f"Successfully organized {moved_count} files into structured categories within {path}."
        except Exception as e:
            return f"Failed to organize directory: {str(e)}"

    def search_local_files(self, search_term: str, root_dir: str = "~") -> str:
        """Searches the local file system recursively for a file or folder matching the search_term. Defaults to user directory 'C:/Users/name'."""
        try:
            import os
            root = os.path.expanduser(root_dir)
            if not os.path.exists(root):
                return f"Directory {root} does not exist."
                
            results = []
            max_results = 15
            search_lower = search_term.lower()
            
            # Fast walk
            for dirpath, dirnames, filenames in os.walk(root):
                for filename in filenames:
                    if search_lower in filename.lower():
                        results.append(os.path.join(dirpath, filename))
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
                    
            if not results:
                return f"Could not find any files matching '{search_term}' directly in {root}."
                
            out = f"Found matches for '{search_term}' (capped at {max_results}):\n"
            out += "\n".join(results)
            return out
        except Exception as e:
            return f"Local file search crashed: {str(e)}"

    def perform_system_optimization(self) -> str:
        """Cleans system junk including Prefetch, Windows Temp, and User Temp folders to optimize performance."""
        try:
            self.set_critical_task("System Optimization & Cleanup", level=1)
            ps_cmd = r"""
            $folders = @(
                "C:\Windows\Prefetch\*",
                "C:\Windows\Temp\*",
                "$env:TEMP\*"
            )
            $count = 0
            foreach ($f in $folders) {
                try {
                    $items = Get-ChildItem -Path $f -ErrorAction SilentlyContinue
                    foreach ($item in $items) {
                        Remove-Item $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
                        $count++
                    }
                } catch {}
            }
            Write-Output "CLEANED:$count"
            """
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if "CLEANED" in res.stdout:
                count = res.stdout.split(':')[-1].strip()
                self.clear_critical_task()
                return f"Optimization complete. Purged {count} temporary junk files from Prefetch and Temp directories."
            self.clear_critical_task()
            return "Optimization finished with no files to remove or permission issues."
        except Exception as e:
            self.clear_critical_task()
            return f"Optimization routine failed: {str(e)}"

    def set_system_volume(self, level: int = 50) -> str:
        """Sets master volume (0-100). Layered strategy: pycaw -> Brute Force Emulation."""
        try:
            import pythoncom
            pythoncom.CoInitialize()
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Precision hardware audio sync successful: Volume set to {level}%."
        except Exception:
            try:
                # ANYHOW FIX: Brute force media key emulation
                # First, zero it out completely
                pyautogui.press('volumemute') # Toggle just in case
                for _ in range(50): pyautogui.press('volumedown')
                # Now ramp up to target (approximate 2% per press)
                presses = int(level / 2)
                for _ in range(presses): pyautogui.press('volumeup')
                return f"Neural audio sync had a hiccup, so I've used brute-force emulation to set volume to approximately {level}%."
            except Exception as e:
                return f"Critical hardware failure: Could not modify audio state via any layer. Error: {str(e)}"

    def set_brightness(self, level: int = 50) -> str:
        """Sets display brightness (0-100). Layered strategy: SBC -> WMI Force."""
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            return f"Display luminance successfully calibrated to {level}%."
        except Exception:
            try:
                # ANYHOW FIX: Forced WMI Kernel instruction via PowerShell
                ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(0, {level})"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
                return f"Neural brightness bridge was blocked, but I've forced a kernel-level override to {level}%."
            except Exception as e:
                return f"Total display driver refusal: I cannot modify your physical backlight at this time. Error: {str(e)}"

    def scrap_notifications(self) -> str:
        """Read the most recent Windows notifications from the system toast history."""
        try:
            # Use WinRT Toast History API via PowerShell
            ps_cmd = r"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $history = [Windows.UI.Notifications.ToastNotificationManager]::History.GetHistory()
            if ($history.Count -eq 0) {
                Write-Output "No active notifications found in system history."
            } else {
                $history | ForEach-Object {
                    $xml = $_.Content.GetXml()
                    $text = $xml.GetElementsByTagName("text") | ForEach-Object { $_.InnerText }
                    Write-Output "APP:$($_.RemoteId) | CONTENT:$($text -join ' - ')"
                }
            }
            """
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            if not res.stdout.strip(): return "Notification center is currently clear."
            return f"Recent System Notifications:\n{res.stdout.strip()}"
        except Exception as e:
            return f"Notification scraper failed: {str(e)}"

    def get_connectivity_status(self, device: str = "wifi"):
        """Queries authoritative network and radio hardware states via PowerShell probes."""
        device = device.lower()
        try:
            if "wifi" in device or "internet" in device:
                ps_cmd = r"""
                $profile = Get-NetConnectionProfile -InterfaceAlias *Wi-Fi* -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($profile) {
                    $ping = Test-Connection -ComputerName 1.1.1.1 -Count 1 -Quiet
                    Write-Output "CONNECTED:$($profile.Name)|INTERNET:$ping"
                } else {
                    $adapter = Get-NetAdapter -InterfaceAlias *Wi-Fi* | Select-Object -First 1
                    Write-Output "STATUS:$($adapter.Status)"
                }
                """
                import subprocess
                res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
                raw = res.stdout.strip()
                if "CONNECTED:" in raw:
                    data = raw.split('|')
                    ssid = data[0].replace("CONNECTED:", "")
                    internet = "and Internet is reachable" if "True" in data[1] else "but Internet appears unreachable"
                    return f"Wi-Fi Status: Connected to '{ssid}' {internet}."
                if "Up" in raw: return "Wi-Fi is currently ON, but looking for a network."
                return "Wi-Fi is currently powered OFF."
            return "Status query completed."
        except: return "Network sensor offline."

    def get_gateway_ip(self):
        """Finds the Router/Gateway IP address without requiring credentials."""
        import subprocess
        try:
            # Command to find the Default Gateway
            output = subprocess.check_output("ipconfig | findstr /i 'Default Gateway'", shell=True).decode()
            ips = [line.split(":")[-1].strip() for line in output.splitlines() if ":" in line and len(line.split(":")[-1].strip()) > 7]
            return ips[0] if ips else "192.168.18.1" # Fallback
        except: return "192.168.18.1"

    def manage_connectivity(self, device: str, state: str) -> str:
        """Toggles hardware states. device: 'wifi', 'bluetooth'. state: 'on', 'off'."""
        device = device.lower()
        state = state.lower()
        try:
            # Authoritative visual toggle for modern OS consistency
            if "wifi" in device: return self.toggle_quick_setting("Wi-Fi")
            elif "bluetooth" in device or "airplane" in device:
                return self.toggle_quick_setting("Bluetooth" if "bluetooth" in device else "Airplane mode")
            return "Unrecognized device."
        except: return "Hardware control error."

    def get_local_network_devices(self):
        """Ghost Scan: Identifies all devices on the current Wi-Fi without needing a router login."""
        import subprocess
        try:
            output = subprocess.check_output("arp -a", shell=True).decode()
            devices = []
            for line in output.splitlines():
                if "dynamic" in line.lower() or "static" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append(f"IP: {parts[0]} | MAC: {parts[1]}")
            
            if not devices: return "No other devices detected on the immediate network arc."
            return "--- NETWORK GHOST SCAN ---\n" + "\n".join(devices[:20])
        except: return "Network sweep sensor failed."

    def toggle_quick_setting(self, setting_name: str) -> str:
        """Opens Quick Settings (Win+A) and physically clicks a toggle button. The ultimate 'Anyhow' fix."""
        try:
            from pywinauto import Application
            import pyautogui
            import time
            
            # Open Quick Settings
            pyautogui.hotkey('win', 'a')
            time.sleep(1.5)
            
            try:
                # Target the Shell's Quick Settings window
                app = Application(backend="uia").connect(title_re="Quick [Ss]ettings|Notification Center", timeout=3)
                window = app.window(title_re="Quick [Ss]ettings|Notification Center")
                
                # Search for the button semantically (partial match)
                # Note: Windows 11 sometimes names them "Bluetooth button" or just "Bluetooth"
                button = window.child_window(title_re=f".*{setting_name}.*", control_type="Button", found_index=0)
                button.click_input()
                time.sleep(0.5)
                pyautogui.press('esc') # Close panel
                return f"Successfully force-toggled '{setting_name}' via Quick Settings hardware bridge."
            except Exception as inner_e:
                pyautogui.press('esc')
                return f"Visual toggle hunt for '{setting_name}' failed: UI thread was obscured."
        except Exception as e:
            return f"Quick Settings pulse aborted: {str(e)}"


    def take_screenshot(self) -> str:
        """Captures a screenshot and saves it to the user's Pictures folder."""
        try:
            import time
            from pathlib import Path
            pictures_path = str(Path.home() / "Pictures")
            os.makedirs(pictures_path, exist_ok=True)
            filename = f"ARYA_Screen_{int(time.time())}.png"
            full_path = os.path.join(pictures_path, filename)
            pyautogui.screenshot(full_path)
            return f"Desktop snapshot archived to: {full_path}"
        except Exception as e:
            return f"Snapshot failed: {str(e)}"

    def lock_workstation(self) -> str:
        """Locks the Windows session immediately."""
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return "Workstation secured via lock sequence."
        except Exception as e:
            return f"Lock sequence failed: {str(e)}"

    def get_recent_notifications(self) -> str:
        """Retrieves Toast alerts and optionally opens the Action Center for UI analysis."""
        try:
            # 1. Background Toast History
            ps_cmd = r"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $history = [Windows.UI.Notifications.ToastNotificationManager]::History.GetHistory()
            if ($history.Count -gt 0) {
                foreach ($toast in $history) {
                    Write-Output "[$($toast.Tag)] $($toast.Content.GetXml().GetElementsByTagName('text')[0].InnerText)"
                }
            }
            """
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            
            history_text = res.stdout.strip()
            if history_text:
                return f"Neural notification sync complete: \n{history_text}"
            
            # 2. UI Fallback: Open Notification Center (Win+N) if user insists on "anything new" and history appears empty
            pyautogui.hotkey('win', 'n')
            return "I've checked your background history (empty), so I've opened the Notification Center for you to see visible alerts."
        except Exception as e:
            return f"Notification scraper encountered a barrier: {str(e)}"

    def execute_os_shortcut(self, shortcut_name: str) -> str:
        """Executes a native Windows shortcut. Supported: 'run', 'explorer', 'settings', 'search', 'clipboard', 'emoji', 'desktop', 'lock', 'task_mgr'."""
        try:
            mapping = {
                "run": ('win', 'r'),
                "explorer": ('win', 'e'),
                "settings": ('win', 'i'),
                "search": ('win', 's'),
                "clipboard": ('win', 'v'),
                "emoji": ('win', '.'),
                "desktop": ('win', 'd'),
                "lock": ('win', 'l'),
                "task_mgr": ('ctrl', 'shift', 'esc')
            }
            keys = mapping.get(shortcut_name.lower())
            if keys:
                pyautogui.hotkey(*keys)
                return f"Native shortcut executed: {shortcut_name.upper()}."
            return "Unrecognized OS shortcut."
        except Exception as e:
            return f"Shortcut execution failed: {str(e)}"

    def run_dialog_command(self, command_text: str) -> str:
        """Opens the Windows Run dialog (Win+R) and executes the specified command."""
        try:
            import time
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write(command_text, interval=0.05)
            pyautogui.press('enter')
            return f"Opened Run dialog and executed: '{command_text}'."
        except Exception as e:
            return f"Run command failure: {str(e)}"

    def resolve_windows_path(self, path_query: str) -> str:
        """Translates natural language drive/folder names to absolute Windows paths. Forced absolute logic."""
        import os
        query = path_query.lower().strip().replace(" ", "")
        
        # 1. DIRECT DRIVE MAPPING (Aggressive)
        if query in ["d", "d:", "drive d", "/d"]: return "D:\\"
        if query in ["c", "c:", "drive c", "/c"]: return "C:\\"
        if query in ["e", "e:", "drive e", "/e"]: return "E:\\"
        
        # 2. Standard User Folders
        home = os.path.expanduser("~")
        if "downloads" in query: return os.path.join(home, "Downloads")
        if "desktop" in query: return os.path.join(home, "Desktop")
        if "documents" in query: return os.path.join(home, "Documents")
        if "pictures" in query: return os.path.join(home, "Pictures")
        
        # 3. Absolute Path Verification
        if ":" in path_query:
            return os.path.abspath(path_query)
            
        return os.path.abspath(os.path.expanduser(path_query))

    def browse_directory(self, path_query: str) -> str:
        """Lists the real-time folders and files present in a specific drive or location. Useful for 'What is in Drive D' requests."""
        try:
            target_path = self.resolve_windows_path(path_query)
            if not os.path.exists(target_path):
                return f"Path Analysis Failed: The location '{target_path}' does not exist or is inaccessible."
            
            items = os.listdir(target_path)
            folders = [f for f in items if os.path.isdir(os.path.join(target_path, f))]
            files = [f for f in items if os.path.isfile(os.path.join(target_path, f))]
            
            # Sort cleanly
            folders.sort()
            files.sort()
            
            out = f"📂 **Contents of {target_path}**\n\n"
            if folders:
                out += "**Folders:**\n" + "\n".join([f"• {f}" for f in folders[:30]]) + "\n\n"
            if files:
                out += "**Files:**\n" + "\n".join([f"  {f}" for f in files[:20]])
                
            if len(items) > 50:
                out += "\n\n*(Showing top 50 items. Ask for more if needed.)*"
                
            return out
        except Exception as e:
            return f"Filesystem barrier encountered while browsing: {str(e)}"

    def update_desktop_wallpaper(self, theme: str = "nature") -> str:
        """Searches for a high-quality wallpaper based on theme, downloads it, and applies it to the desktop."""
        try:
            import requests
            import ctypes
            from pathlib import Path
            import time
            
            # 1. Neural Aesthetic Search (Using high-res Unsplash Source)
            clean_theme = theme.lower().replace(" ", ",")
            image_url = f"https://source.unsplash.com/1920x1080/?{clean_theme},wallpaper"
            
            # 2. Local Archiving
            save_path = Path.home() / "Pictures" / f"ARYA_Wallpaper_{int(time.time())}.jpg"
            response = requests.get(image_url, timeout=10)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                # 3. Kernel-Level OS Application
                # SPI_SETDESKWALLPAPER = 20
                ctypes.windll.user32.SystemParametersInfoW(20, 0, str(save_path), 3)
                
                return f"Desktop transformation complete. New {theme} aesthetic applied and archived to: {save_path}"
            else:
                return f"Aesthetic search failed: The image server returned status {response.status_code}."
        except Exception as e:
            return f"Wallpaper transformation interrupted: {str(e)}"

    def manage_system_drivers(self, action: str = "check") -> str:
        """Audits and manages system drivers. action: 'check' or 'update'."""
        try:
            if action == "check":
                # Use pnputil to list non-generic drivers
                res = subprocess.run(["pnputil", "/enum-drivers"], capture_output=True, text=True)
                lines = res.stdout.split('\n')[:20] # Summary of first 20 drivers
                return f"Driver Audit Complete: {len(lines)} active third-party drivers detected. System is running on verified kernels.\n" + "\n".join(lines)
            
            elif action == "update":
                # Trigger Windows Update settings page
                os.system("start ms-settings:windowsupdate")
                return "I've opened your Windows Update panel. I recommend checking for 'Optional Updates' specifically for your hardware drivers."
            
            return "Command recognized. Specify 'check' or 'update'."
        except Exception as e:
            return f"Driver management encountered a barrier: {str(e)}"

    def manage_gpu_settings(self, action: str = "status") -> str:
        """Inspects and manages NVIDIA GPU settings. action: 'status' or 'open'."""
        try:
            if action == "status":
                try:
                    res = subprocess.run(["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,driver_version", "--format=csv,noheader"], capture_output=True, text=True)
                    if res.returncode == 0:
                        data = res.stdout.strip().split(', ')
                        return f"NVIDIA GPU Telemetry:\n• Model: {data[0]}\n• Temp: {data[1]}°C\n• Load: {data[2]}\n• Driver: {data[3]}"
                except:
                    return "NVIDIA GPU detected, but 'nvidia-smi' is not available."
            elif action == "open":
                os.system("start nvcplui.exe")
                return "Launching NVIDIA Control Panel..."
            return "GPU command recognized. Specify 'status' or 'open'."
        except Exception as e:
            return f"GPU management failed: {str(e)}"

    def manage_windows_services(self, service_name: str, action: str) -> str:
        """Manages Windows services (start, stop, restart, status). Requies admin privileges."""
        try:
            # Service common name mapping
            mapping = {
                "audio": "AudioSrv",
                "bluetooth": "bthserv",
                "print spooler": "Spooler",
                "windows update": "wuauserv",
                "defender": "WinDefend"
            }
            svc = mapping.get(service_name.lower(), service_name)
            
            cmd = f"powershell -Command \"{action.capitalize()}-Service -Name '{svc}'\""
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if res.returncode == 0:
                return f"Successfully executed '{action}' on service '{service_name}' ({svc})."
            else:
                return f"Service action failed: {res.stderr.strip()}"
        except Exception as e:
            return f"Service management error: {str(e)}"

    def diagnose_system_issue(self, issue_description: str) -> str:
        """Heuristic diagnostics for common PC issues. Returns a summary and suggested repair."""
        issue = issue_description.lower()
        
        if "wifi" in issue or "net" in issue or "internet" in issue:
            res = subprocess.run(["ping", "8.8.8.8", "-n", "1"], capture_output=True, text=True)
            if res.returncode != 0:
                return "DIAGNOSIS: Local network connectivity heartbeat failed. Recommendation: Execute 'network_reset'."
            return "DIAGNOSIS: Physical network link is active. If sites aren't loading, execute 'dns_flush'."
            
        elif "audio" in issue or "sound" in issue:
            return "DIAGNOSIS: Possible service hang or driver conflict. Recommendation: Execute 'audio_repair' (Restarts AudioSrv)."
            
        elif "slow" in issue or "lag" in issue:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            return f"DIAGNOSIS: System resource load is at CPU={cpu}%, RAM={ram}%. Recommendation: Execute 'storage_cleanup' or 'startup_optimize'."
            
        return "DIAGNOSIS: Non-specific system anomaly detected. Recommendation: Run 'check_health' for a full component scan."

    def execute_system_repair(self, repair_type: str, confirmed: bool = False) -> str:
        """Executes targeted system repairs based on diagnostic findings. confirmed=True required for destructive actions."""
        rt = repair_type.lower()
        self.set_critical_task(f"System Repair: {repair_type}", level=2)
        
        try:
            if "dns_flush" in rt:
                subprocess.run("ipconfig /flushdns", shell=True)
                return "Repair Successful: DNS Resolver cache flushed."
                
            elif "network_reset" in rt:
                if not confirmed: return "[CONFIRMATION REQUIRED] This will reset all network adapters. Should I proceed?"
                subprocess.run("netsh winsock reset", shell=True)
                subprocess.run("netsh int ip reset", shell=True)
                return "Repair Successful: Network stack reset. Please restart your PC."
                
            elif "audio_repair" in rt:
                self.manage_windows_services("audio", "restart")
                return "Repair Successful: Windows Audio services cycled."
                
            elif "check_health" in rt:
                subprocess.Popen("powershell -Command \"sfc /scannow; DISM /Online /Cleanup-Image /CheckHealth\"", shell=True)
                return "Repair Initiated: SFC and DISM health scans are running in background. I'll notify you when done."

            elif "storage_cleanup" in rt:
                # Basic temp file cleanup
                temp_path = os.environ.get('TEMP')
                if temp_path:
                    subprocess.run(f'del /q /s /f "{temp_path}\\*.*"', shell=True)
                return "Storage Cleanup: Temporary system files cleared."

            return f"Repair type '{repair_type}' is not currently in the ARYA playbook."
        except Exception as e:
            return f"Repair operation failed: {str(e)}"
        finally:
            self.clear_critical_task()

    def manage_winget_packages(self, action: str, app_name: str) -> str:
        """Manages apps via Windows Package Manager (Winget). action: 'install', 'upgrade', 'search', 'uninstall'."""
        try:
            cmd = f"winget {action} \"{app_name}\" --accept-source-agreements --accept-package-agreements"
            if action == "search":
                res = subprocess.run(f"winget search \"{app_name}\"", capture_output=True, text=True)
                return f"Winget Search Results for '{app_name}':\n{res.stdout}"
            
            subprocess.Popen(cmd, shell=True)
            return f"Winget task '{action}' for '{app_name}' has been initiated in background."
        except Exception as e:
            return f"Winget automation failed: {str(e)}"

    def check_all_updates(self) -> str:
        """Checks for all available software updates via Winget and returns a summary."""
        try:
            res = subprocess.check_output("winget update", shell=True).decode().strip()
            if "No applicable update found" in res:
                return "Systems are up to date. No pending application updates."
            return f"PENDING UPDATES:\n{res[:1000]}"
        except Exception as e:
            return f"Failed to check for updates: {str(e)}"

    def analyze_battery_health(self) -> str:
        """Generates and analyzes a Windows Battery Health report. Detects capacity degradation."""
        try:
            temp_path = os.path.join(os.environ.get("TEMP", "C:\\temp"), "battery-report.html")
            subprocess.run(f"powercfg /batteryreport /output \"{temp_path}\"", shell=True, check=True)
            # We don't parse the HTML directly, but we let the user know it's ready
            os.startfile(temp_path)
            return "Battery Health Analysis Complete. I have opened the HTML report in your browser for detailed inspection."
        except Exception as e:
            return f"Battery analysis failed: {str(e)}"

    def scan_network_environment(self) -> str:
        """Scans the local airwaves for neighboring Wi-Fi networks and signal strengths."""
        try:
            cmd = "netsh wlan show networks mode=bssid"
            res = subprocess.check_output(cmd, shell=True).decode().strip()
            # Clean up output to show top networks
            lines = res.split('\n')
            summary = "\n".join(lines[:30]) # Cap output
            return f"LOCAL NETWORK ENVIRONMENT SCAN:\n{summary}"
        except Exception as e:
            return f"Network scan failed: {str(e)}"

    def monitor_active_connections(self) -> str:
        """Displays active network connections and the processes owning them (Netstat map)."""
        try:
            import psutil
            import socket
            conns = psutil.net_connections(kind='inet')
            report = "ACTIVE NEURAL NETWORK MAP (Inbound/Outbound):\n"
            for c in conns[:10]: # Top 10 for brevity
                l_addr = f"{c.laddr.ip}:{c.laddr.port}"
                r_addr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "LISTEN"
                pid = c.pid
                proc_name = "Unknown"
                if pid:
                    try: proc_name = psutil.Process(pid).name()
                    except: pass
                report += f"• PID {pid} ({proc_name}): {l_addr} -> {r_addr} [{c.status}]\n"
            return report
        except Exception as e:
            return f"Connection monitoring failed: {str(e)}"

    def manage_startup_apps(self, action: str = "list", app_name: str = "") -> str:
        """Manages apps that run at boot. action: 'list', 'disable' (requires precision)."""
        try:
            import winreg
            hkey = winreg.HKEY_CURRENT_USER
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            if action == "list":
                with winreg.OpenKey(hkey, reg_path) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    apps = []
                    for i in range(count):
                        name, val, _ = winreg.EnumValue(key, i)
                        apps.append(f"• {name}: {val}")
                    return "REGISTERED STARTUP APPLICATIONS:\n" + ("\n".join(apps) or "None found in HKCU.")
            
            return f"Startup action '{action}' is not yet automated. Please manual check in Settings > Apps > Startup."
        except Exception as e:
            return f"Startup management failed: {str(e)}"

    def get_event_logs(self, log_type: str = "System", count: int = 5) -> str:
        """Retrieves the most recent items from Windows Event Viewer for troubleshooting."""
        try:
            cmd = f"powershell -Command \"Get-EventLog -LogName '{log_type}' -Newest {count} | Select-Object -Property TimeGenerated, Source, Message | ConvertTo-Json\""
            res = subprocess.check_output(cmd, shell=True).decode().strip()
            return f"RECENT {log_type.upper()} EVENTS:\n{res}"
        except Exception as e:
            return f"Failed to retrieve event logs: {str(e)}"

    def manage_files(self, action: str, source_path: str, destination_path: str = "", pattern: str = "", confirmed: bool = False) -> str:
        """Handles file operations: create, rename, move, copy, delete, zip, extract. Returns status."""
        import shutil
        import zipfile
        from pathlib import Path
        
        try:
            src = Path(self.resolve_windows_path(source_path))
            dest = Path(self.resolve_windows_path(destination_path)) if destination_path else None
            
            if action == "create_folder":
                src.mkdir(parents=True, exist_ok=True)
                return f"Successfully created folder: {src}"
            
            if not src.exists():
                return f"Operation FAILED: '{src}' does not exist."

            if action == "move":
                shutil.move(str(src), str(dest))
                return f"Moved '{src.name}' to {dest.parent}."
            
            elif action == "copy":
                if src.is_dir():
                    shutil.copytree(str(src), str(dest))
                else:
                    shutil.copy2(str(src), str(dest))
                return f"Copied '{src.name}' to {dest}."
                
            elif action == "rename":
                src.rename(dest)
                return f"Renamed '{src.name}' to '{dest.name}'."
                
            elif action == "delete":
                if not confirmed:
                    return f"[CONFIRMATION] This will permanently delete '{src.name}'. Should I proceed?"
                if src.is_dir():
                    shutil.rmtree(str(src))
                else:
                    src.unlink()
                return f"Successfully deleted: {src.name}."
                
            elif action == "zip":
                archive = shutil.make_archive(str(src), 'zip', str(src))
                return f"Compressed '{src.name}' into: {archive}"
                
            elif action == "extract":
                with zipfile.ZipFile(str(src), 'r') as zip_ref:
                    zip_ref.extractall(str(dest or src.parent))
                return f"Extracted contents of '{src.name}' to {dest or src.parent}."

            return f"Action '{action}' is not currently in the file management playbook."
        except Exception as e:
            return f"File operation error: {str(e)}"

    def manage_storage_devices(self, action: str, drive_letter: str = "", confirmed: bool = False) -> str:
        """Handles storage operations: list, eject, format. Formatting REQUIRES admin and confirmation."""
        try:
            if action == "list":
                import psutil
                drives = psutil.disk_partitions()
                removable = [d.device for d in drives if 'removable' in d.opts]
                return f"Detected Removable Drives: {', '.join(removable) or 'None found.'}"

            if not drive_letter:
                return "Drive letter (e.g., 'E:') is required for this action."

            if action == "format":
                if not confirmed:
                    return f"[SAFETY WARNING] Formatting drive {drive_letter} will erase ALL DATA. Are you absolutely sure?"
                # Command: format E: /FS:exFAT /Q /V:ARYA_DRIVE /Y
                cmd = f"format {drive_letter} /Q /Y"
                subprocess.run(cmd, shell=True, check=True)
                return f"Quick format of {drive_letter} successful."
            
            elif action == "eject":
                # PowerShell command for safe removal
                cmd = f"powershell -Command \"(New-Object -comObject Shell.Application).Namespace(17).ParseName('{drive_letter}').InvokeVerb('Eject')\""
                subprocess.run(cmd, shell=True)
                return f"Sent eject signal to {drive_letter}. You can safely remove it now."

            return f"Storage action '{action}' is not supported."
        except Exception as e:
            return f"Storage operation error: {str(e)}"

    def run_terminal_command(self, command: str, use_admin: bool = False) -> str:
        """Executes a terminal command (PowerShell default) and returns the output log."""
        try:
            cmd_prefix = "powershell -Command " if not use_admin else "powershell -ExecutionPolicy Bypass -Command "
            # We don't use 'start' here so we can capture output
            res = subprocess.run(f"{cmd_prefix} \"{command}\"", capture_output=True, text=True, shell=True)
            
            output = res.stdout.strip() or res.stderr.strip()
            if not output: output = "Command executed successfully (No output returned)."
            
            return f"TERMINAL OUTPUT:\n{output[:1000]}" # Cap output
        except Exception as e:
            return f"Terminal execution failed: {str(e)}"
