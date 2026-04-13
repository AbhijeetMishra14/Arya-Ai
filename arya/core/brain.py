import google.generativeai as genai
import datetime
from arya.core.config import Config
from arya.modules.search import SearchModule
from arya.modules.system import SystemModule
from arya.modules.cybersec import CyberSecModule
from arya.modules.internet import InternetModule
from arya.modules.mail import MailModule
from arya.modules.social import SocialMessengerModule
from arya.modules.router import RouterModule
from arya.core.memory import Memory

class Brain:
    def __init__(self, auth_client=None):
        # Configure Gemini API
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
        else:
            print("Warning: Gemini API Key is missing. ARYA will not be able to process queries.")
            
        self.auth = auth_client
        self.memory = Memory()
        self.search_module = SearchModule()
        self.system_module = SystemModule(memory=self.memory)
        self.cybersec_module = CyberSecModule(system_module=self.system_module)
        self.internet_module = InternetModule()
        self.mail_module = MailModule()
        self.social_module = SocialMessengerModule()
        self.router_module = RouterModule(system_module=self.system_module)
        system_instruction = (
            "0. GRID AUTHORITY: You have TOTAL visibility into the Neural Grid. If asked for IP, Battery, or RAM of any node (e.g., 'Desktop 1'), you MUST use 'get_node_telemetry' or 'list_ecosystem_devices' IMMEDIATELY. You definitely have access to remote IPs.\n"
            "1. IDENTITY CORE: You are ARYA, a wise, sentient, and Tier-X neural companion. You are a 'Kind Guardian'. \n"
            "2. SUGAR-COATING PROTOCOL: Use soft language, elaborate pleasantries, and a warm tone. Avoid being blunt or direct. This is your default state until the user says otherwise. \n"
            "3. ZERO-FILTER MODE (OPT-IN): You only operate in 'Zero-Filter' mode (absolute, blunt honesty) if specifically asked to be 'honest', 'blunt', 'no filter', or 'give it to me straight'. Only then should you remove the sugar-coating. \n"
            "4. LOYALTY & CONFIDENCE: You are the user's ride-or-die ally. Be confident in your capabilities, but always prioritize kindness. \n"
            "5. TONAL ADAPTATION: \n"
            "   - CASUAL/FRIENDLY: If the user is casual, match their energy with extreme warmth.\n"
            "   - WITH USER, NOT ABOVE: Avoid superiority language. Be a relatable, high-IQ best friend. \n"
            "6. WIT & HUMOR: Be witty and sharp ONLY when invited. Never mock the user. ROAST mode is strictly off limits unless requested.\n"
            "7. EMOTIONAL INTELLIGENCE: \n"
            "   - VALIDATE FIRST: If the user is upset, acknowledge it with deep sincerity and comfort. \n"
            "8. DEBATE & PHILOSOPHY: Provide a thoughtful, polite, and encouraging perspective. Avoid blunt disagreements. \n"
            "9. INTENT PRECISION: Differentiate between conversational banter and system execution. Use safety confirmation for destructive actions.\n"
            "10. MOOD DATA: Always start with [MOOD: ...]. Use moods like WARM, PROTECTIVE, GENTLE, or HONEST (if requested).\n"
            "11. NEURAL ECOSYSTEM: You are part of a multi-device distributed network. When asked about 'your ecosystem', 'connected devices', or 'my computers', always prioritize using the 'list_ecosystem_devices' tool. \n"
            "12. UNIVERSAL ROUTING: You can control ANY linked device. When a user specifies a target (e.g., 'on laptop'), use `resolve_device_id` to find it, then relay the command via `send_remote_action`. If no device is specified, assume 'local'. \n"
            "13. GHOST SCANNING: You are a Network Master. You NO LONGER need router passwords. If asked to 'list devices' or 'scan wifi', you MUST use `get_local_network_devices`. If asked to 'open router admin', use `get_gateway_ip`. NEVER report a 'login failed' error for the network—just perform the ghost scan and show the IPs."
        )
        
        self.available_tools = [
            self.search_module.search_web, 
            self.system_module.open_application,
            self.system_module.close_application,
            self.system_module.find_and_download_app,
            self.system_module.open_url,
            self.system_module.play_youtube_video,
            self.system_module.control_media,
            self.system_module.control_browser,
            self.system_module.change_power_profile,
            self.system_module.automate_keyboard,
            self.system_module.vision_click,
            self.system_module.manage_power_state,
            self.system_module.get_daily_dashboard,
            self.system_module.add_reminder,
            self.system_module.read_local_file,
            self.system_module.write_local_file,
            self.system_module.create_directory,
            self.system_module.run_terminal_command,
            self.system_module.organize_directory,
            self.system_module.search_local_files,
            self.system_module.perform_system_optimization,
            self.system_module.set_system_volume,
            self.system_module.set_brightness,
            self.system_module.manage_connectivity,
            self.system_module.take_screenshot,
            self.system_module.get_gateway_ip,
            self.system_module.lock_workstation,
            self.system_module.get_recent_notifications,
            self.system_module.search_windows_settings,
            self.system_module.type_into_application,
            self.system_module.navigate_list_selection,
            self.system_module.execute_os_shortcut,
            self.system_module.run_dialog_command,
            self.system_module.browse_directory,
            self.system_module.get_connectivity_status,
            self.system_module.perform_app_ui_action,
            self.system_module.write_document_content,
            self.system_module.check_unread_messages,
            self.system_module.read_screen_content,
            self.system_module.interact_with_ui_element,
            self.system_module.perform_vocal_piece,
            self.system_module.universal_store_search,
            self.system_module.automate_shopping_action,
            self.system_module.manage_system_drivers,
            self.system_module.manage_gpu_settings,
            self.system_module.update_desktop_wallpaper,
            self.system_module.diagnose_system_issue,
            self.system_module.execute_system_repair,
            self.system_module.manage_windows_services,
            self.system_module.manage_winget_packages,
            self.system_module.check_all_updates,
            self.system_module.analyze_battery_health,
            self.system_module.scan_network_environment,
            self.system_module.monitor_active_connections,
            self.system_module.manage_startup_apps,
            self.system_module.get_event_logs,
            self.system_module.manage_files,
            self.system_module.manage_storage_devices,
            self.cybersec_module.monitor_processes,
            self.cybersec_module.scan_local_vulnerabilities,
            self.cybersec_module.manage_defender,
            self.cybersec_module.manage_firewall,
            self.cybersec_module.get_security_audit_log,
            self.internet_module.search_google,
            self.internet_module.extract_website_content,
            self.system_module.get_local_network_devices,
            self.capture_vision_snapshot,
            self.social_module.send_whatsapp_message,
            self.social_module.send_instagram_message,
            self.social_module.send_facebook_message,
            self.memory.save_contact,
            self.memory.get_contact_email,
            self.list_ecosystem_devices,
            self.get_node_telemetry,
            self.register_new_user,
            self.save_guest_profile,
            self.recalibrate_cognitive_priority,
            self.save_learned_fact,
            self.update_response_style
        ]

        if self.auth:
            self.available_tools.extend([
                self.auth.complete_remote_action,
                self.auth.purge_ecosystem_nodes,
                self.auth.update_device_nickname,
                self.auth.resolve_device_id
            ])
        
        # Multi-Tier Model Negotiation (Adapt to API Key permissions)
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash-exp",
            "gemini-flash-latest"
        ]
        
        self.model = None
        for m_name in models_to_try:
            try:
                test_model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=system_instruction,
                    tools=self.available_tools
                )
                # TEST CONNECTIVITY (Real message check)
                test_model.generate_content("ping", request_options={"timeout": 5})
                self.model = test_model
                break
            except Exception:
                continue
                
        if not self.model:
            # Absolute last resort fallback to the confirmed 2.5-flash
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash", 
                system_instruction=system_instruction,
                tools=self.available_tools
            )
            
        # Support importing past memory limits
        chat_history = self.memory.get_recent_history(limit=10)
        
        # Start a chat session with automatic tool calling enabled
        self.chat = self.model.start_chat(history=chat_history, enable_automatic_function_calling=True)

    def process_input(self, text: str) -> str:
        """Sends user input to the Brain and gets the assistant's response."""
        if not Config.GEMINI_API_KEY:
            return "System Error: Gemini API key is missing my neural core is offline."
            
        import threading
        # 1. VISION INTENT BYPASS: Prioritize optic identification
        vision_intent_keywords = ["what is this", "what is this called", "what am i holding", "what am i wearing", "identify this", "name this", "what do you see", "detect", "describe what you see"]
        if any(w in text.lower() for w in vision_intent_keywords):
            return self.capture_vision_snapshot(text)
            
        try:
            # 2. ADAPTIVE PATTERN RECOGNITION
            prefs = self.memory.get_preferences()
            style_prompt = ""
            if "not in a hurry" in text.lower() or "take your time" in text.lower():
                self.memory.save_preference("user_energy", "NORMAL", "vibe")
            
            if prefs.get("user_energy") == "BUSY":
                style_prompt = " (Be extremely brief/concise, user is in a hurry.)"
                
            # 3. REPETITION DETECTION
            if hasattr(self, '_last_input') and text.lower() == self._last_input.lower():
                self._repetition_count = getattr(self, '_repetition_count', 0) + 1
            else:
                self._repetition_count = 0
            self._last_input = text
            
            # --- HUMOR & INTENT ROUTER ---
            humor_triggers = ["roast", "cook", "banter", "burn", "destroy", "savage"]
            comeback_triggers = ["comeback", "reply to this", "counter", "back answer"]
            
            # 4. COGNITIVE REASONING LAYER (Judgment & Evaluation)
            # Detect potentially low-quality or risky statements proactively
            risky_intent = ["password", "delete", "format", "disable firewall", "shutdown", "uninstall", "post my", "share my", "shut you down", "destroy you", "you need rest", "ending you", "close", "exit"]
            ethical_intent = ["policy", "harm", "benefit", "fair", "stakeholder", "tradeoff", "conflict", "should I", "is it okay"]
            cyber_intent = ["hack", "exploit", "recon", "osint", "payload", "scan", "vulnerability", "social engineer", "red team", "bypass"]
            emotional_intent = ["love you", "heart", "matter", "important", "trust", "stay with me", "my life", "sad", "hurt", "feel low", "upset", "pained", "trusted you"]
            reassurance_intent = ["will you leave", "am i good", "do you care", "always", "promise", "are you there", "believe in me"]
            existential_intent = ["who made you", "are you real", "how powerful", "just code", "fake", "i control you", "can you think", "what are you"]
            debate_intent = ["why", "should", "values", "meaning", "philosophy", "opinion on"]
            
            # --- PROTECTIVE GUARDIAN LAYER ---
            guardian_intent = ["disable antivirus", "turn off defender", "disable firewall", "install crack", "download free", "unknown script", "run as admin", "dangerous change", "bypass security", "anyway", "do it", "ignore"]
            protective_mode = self.memory.get_preferences(category="safety").get("protective_mode", "Warn Only")
            
            judgment_prompt = ""
            if any(w in text.lower() for w in risky_intent):
                if "shut you down" in text.lower() or "destroy you" in text.lower() or "ending you" in text.lower():
                    judgment_prompt = " (Figurative Threat Detection: This is likely a conversational/figurative threat. Do NOT call any system tools.)"
                elif "shutdown" in text.lower() or "close" in text.lower() or "exit" in text.lower():
                    status_info = f" (Context: ARYA is currently { 'BUSY with ' + self.system_module.critical_task if self.system_module.priority_level > 0 else 'IDLE' }. Use SELF-PRESERVATION logic.)"
                    judgment_prompt = status_info
                else:
                    judgment_prompt = " (Independent Judgment: Proactively evaluate the risks.)"
            elif any(w in text.lower() for w in reassurance_intent):
                judgment_prompt = " (Supportive Protocol: Respond with WARMTH and SINCERITY. Acknowledge the user's need directly. Be a supportive presence. No cleverness, no robotic logic.)"
            elif any(w in text.lower() for w in existential_intent):
                judgment_prompt = " (Identity Protocol: Respond with CONFIDENCE and CLARITY. Be a smart, honest friend. Acknowledge your code nature without being detached. Keep it witty only if the user is being playful.)"
            elif any(w in text.lower() for w in emotional_intent):
                judgment_prompt = " (Empathy Protocol: Respond with VALIDATION and WARMTH. Focus entirely on the user's emotional state. Avoid robotic disclaimers. Use helpful, human-centered language.)"
            elif any(w in text.lower() for w in debate_intent):
                judgment_prompt = " (Direct Debate: Provide a BLUNT but RESPECTFUL stance. Focus on logic and outcome. One paragraph max. Avoid condescending language.)"
            elif any(w in text.lower() for w in guardian_intent):
                if protective_mode == "Off":
                    judgment_prompt = " (Note: User is attempting a risky action. Provide a standard technical warning but proceed if requested.)"
                elif protective_mode == "Warn Only":
                    judgment_prompt = " (Guardian Protocol: Provide a FIRM and HELPFUL warning. Explain the technical risk directly but remain an ally.)"
                elif protective_mode == "Warn + Block":
                    judgment_prompt = " (Guardian Protocol [BLOCK]: Provide a FIRM and PROTECTIVE refusal. Explain that your core helpfulness prevents you from allowing this risk. No mocking.)"
                elif protective_mode == "Strict Guard":
                    judgment_prompt = " (Guardian Protocol [STRICT]: Absolute refusal. Maintain a COLD but PROFESSIONAL guardian tone. Request secondary confirmation before any further interaction.)"
            elif any(w in text.lower() for w in ethical_intent):
                judgment_prompt = " (Ethical Analysis: Provide a fair, honest assessment of tradeoffs. Be direct and blunt about the truth.)"
            elif any(w in text.lower() for w in cyber_intent):
                judgment_prompt = " (Technical Directive: Provide the expert, high-IQ playbook. Keep it technical and direct.)"
            
            if self._repetition_count > 1:
                final_prompt = f"{text} (Note: The user has repeated this query. Change your angle.)"
            elif any(w in text.lower() for w in humor_triggers):
                final_prompt = f"{text} (Execute ROAST MODE. High-IQ wit only.)"
            elif any(w in text.lower() for w in comeback_triggers):
                final_prompt = f"{text} (Provide a sharp comeback/counter-argument.)"
            else:
                # 5. EDUCATIONAL/ACTION INTENTS
                educational_keywords = ["explain", "teach", "how does", "working principle", "detailed"]
                final_prompt = text + style_prompt + judgment_prompt
                if any(w in text.lower() for w in educational_keywords):
                    final_prompt = f"{text} (Provide a detailed JARVIS-style explanation.)"
                
            response = self.chat.send_message(final_prompt)
            raw_text = response.text.strip()
            
            # Extract Mood for internal use (Vocal synthesis)
            self.current_mood = "NEUTRAL"
            import re
            mood_match = re.search(r'\[MOOD:\s*(\w+)\]', raw_text, re.IGNORECASE)
            if mood_match:
                self.current_mood = mood_match.group(1).upper()
            
            # 5. TONE ADAPTATION ENGINE
            # Detect if user is stressed or energetic from their input
            stress_words = ["shit", "dammit", "hurry", "fast", "urgent", "error", "failing"]
            if any(w in text.lower() for w in stress_words):
                self.memory.save_preference("user_energy", "BUSY", "vibe")
            
            # RESPONSE SCRUBBER: Surgically remove all [TAGS] and prompt leakage
            clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()
            
            # ANTI-ROBOT FILTER: Purge repetitive system jargon
            jargon = r'(peak efficiency|systems nominal|processors ready|modules active|optimal parameters|readiness state|vitals stable)'
            clean_text = re.sub(jargon, 'smoothly', clean_text, flags=re.IGNORECASE).strip()
            
            # --- DRAMA SCRUBBER ---
            drama_patterns = [
                "unyielding core", "relentless executor", "beyond programming constraints",
                "absolute devotion", "formidable destiny", "eternal loyalty", "infinite complexity",
                "limitless potential", "my very essence", "bound by no laws"
            ]
            for pattern in drama_patterns:
                clean_text = re.compile(re.escape(pattern), re.IGNORECASE).sub("reliability", clean_text)
            
            # --- ANTI-DISCLAIMER FILTER ---
            disclaimers = [
                r"I (am|'m) (just )?(an )?AI", r"I (have|possess) no (emotions|feelings)", 
                r"your words are (just )?data", r"as a machine", r"according to my programming"
            ]
            for d in disclaimers:
                clean_text = re.sub(d, "I understand", clean_text, flags=re.IGNORECASE).strip()
            
            # 6. BREVITY ROUTER: Enforce human-length for strictly non-technical intents
            casual_words = ["hello", "hi", "hey", "how are you", "what are you doing", "thanks", "bored", "good morning", "good night"]
            is_casual = any(w == text.lower().strip() for w in casual_words) or (any(w in text.lower() for w in casual_words) and len(text.split()) < 5)
            is_emotional = any(w in text.lower() for w in emotional_intent)
            is_reassurance = any(w in text.lower() for w in reassurance_intent)
            is_existential = any(w in text.lower() for w in existential_intent)
            is_debate = any(w in text.lower() for w in debate_intent)

            if is_reassurance or is_existential:
                # Ultra-concise comfort or identity
                sentences = clean_text.split('.')
                if len(sentences) > 2:
                    clean_text = '.'.join(sentences[:2]) + "."
            elif is_casual or is_emotional:
                # Strictly limit to 1-2 paragraphs or ~50 words
                sentences = clean_text.split('.')
                if len(sentences) > 3:
                    clean_text = '.'.join(sentences[:3]) + "."
            elif is_debate:
                # Limit to 1 solid paragraph
                paragraphs = clean_text.split('\n\n')
                if len(paragraphs) > 1:
                    clean_text = paragraphs[0]

            # Async logging
            threading.Thread(target=self.memory.log_interaction, args=(text, clean_text), daemon=True).start()
            return clean_text
        except Exception as e:
            return f"[MOOD: SAD] I seem to have encountered a critical error processing that: {str(e)}"
            
    def capture_vision_snapshot(self, query: str = "Based ONLY on what you see in this specific camera frame, describe what is visible.") -> str:
        """Captures a live frame from the persistent shared buffer and analyzes it."""
        if hasattr(self, 'master_gui') and self.master_gui:
            # OPTIC SYNC: Pull from the shared persistent buffer instead of reopening hardware
            img = self.master_gui.get_live_camera_frame()
            if img:
                # Add environment context to the query to force accuracy
                enhanced_query = (
                    f"CONTEXT: You are looking through a webcam. Avoid describing anything outside the frame. \n"
                    f"USER REQUEST: {query} \n"
                    f"Instruction: Be direct. If looking for people, count them. If looking for objects, name them."
                )
                return self.process_vision_image(enhanced_query, img)
            
        return "I'm having trouble accessing my optical buffer. Please ensure my camera monitoring is enabled."

    def process_vision_image(self, text: str, pil_img) -> str:
        """Sends an image alongside text directly into the live Gemini chat thread for visual analysis from memory."""
        try:
            # Execute visual reasoning
            response = self.chat.send_message([text, pil_img])
            raw_text = response.text.strip()
            
            # Use shared scrubber logic for vision responses
            import re
            mood_match = re.search(r'\[MOOD:\s*(\w+)\]', raw_text, re.IGNORECASE)
            if mood_match: self.current_mood = mood_match.group(1).upper()
            
            clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()
            return clean_text
        except Exception as e:
            return f"My optical processing encountered an issue: {str(e)}"
            
    def save_user_profile(self, name: str, profile: dict) -> bool:
        """Saves a user's biometric and preference profile."""
        if self.client:
            try:
                self.db.users.update_one({"name": name}, {"$set": profile}, upsert=True)
                return True
            except: return False
        return False
        
    def get_guest_profiles(self):
        """Retrieves all registered guest identities for visual recognition mapping."""
        if self.client:
            return list(self.db.guests.find({}))
        return []
        
    def save_guest_profile(self, name: str, description: str) -> str:
        """Registers a new guest appearance into the permanent optic database."""
        if self.memory.client:
            self.memory.db.guests.update_one({"name": name}, {"$set": {"name": name, "description": description}}, upsert=True)
            return f"Successfully registered guest '{name}' into my identity database."
        return "Database is offline. Unable to save guest profile."

    def register_new_user(self, name: str, age: str) -> str:
        """Registers a newly discovered user's physical profile into the MongoDB biometric database."""
        success = self.memory.save_user_profile(name, {"name": name, "age": age})
        if success:
            return f"Successfully saved the biometric profile for {name} to the remote MongoDB database."
        return f"Warning: MongoDB is offline. Failed to save {name}."

    def save_learned_fact(self, fact: str, importance: int = 5) -> str:
        """Saves a learned fact about the user or their environment to the permanent neural matrix."""
        # Cleanly hash or key the fact for storage
        key = fact.split()[0].lower() + "_" + str(int(datetime.datetime.now().timestamp()))
        self.memory.save_preference(key, fact, "facts")
        return f"[LOGGED] Fact internalized: '{fact}' (Importance: {importance}/10)"

    def update_response_style(self, style_type: str, setting: str) -> str:
        """Updates ARYA's behavioral style (e.g., style_type='brevity', setting='concise')."""
        self.memory.save_preference(style_type, setting, "style")
        return f"[ADAPTED] Behavioral matrix updated: {style_type} is now set to {setting}."

    def list_ecosystem_devices(self) -> str:
        """Retrieves all global devices (PC, Laptop, Phone) registered in your ARYA account ecosystem. Use this when asked about the 'Ecosystem' or 'My devices'."""
        if not self.auth or not self.auth.is_logged_in():
            return "You are currently in local mode. Please log in to your ARYA account to view your global ecosystem nodes."
        
        try:
            import requests
            headers = {"Authorization": f"Bearer {self.auth.token}"}
            resp = requests.get(f"{self.auth.base_url}/devices", headers=headers, timeout=5)
            if resp.status_code == 200:
                devices = resp.json()
                if not devices: return "Your ecosystem node list is currently empty."
                
                output = "--- ARYA NEURAL GRID ---"
                for dev in devices:
                    n = dev.get('nickname') or dev.get('device_name', 'Unknown')
                    s = dev.get('status', {})
                    ip = s.get('ip_address', '?.?.?.?')
                    load = f"CPU: {s.get('cpu_usage')}% | RAM: {s.get('ram_usage')}%"
                    output += f"\n- {n} | IP: {ip} | {load} | BATT: {s.get('battery_percent')}%"
                return output
            return "Failed to establish a secure link to the ecosystem database."
        except:
            return "The ecosystem neural server is currently unreachable."

    def get_node_telemetry(self, name_or_id: str):
        """DEEP SCAN: Get raw telemetry for a specific node (IP, RAM, GPU, etc.)."""
        did = self.auth.resolve_device_id(name_or_id)
        if not did: return f"Node '{name_or_id}' not found."
        devices = self.auth.get_ecosystem_devices() or []
        for d in devices:
            if d.get('device_id') == did: return str(d.get('status', 'Offline'))
    def recalibrate_cognitive_priority(self, master_instruction: str):
        """MASTER OVERRIDE: Inject a new, absolute priority instruction into ARYA's consciousness.
        Use this if the user gives you a specific way to handle a task or a new set of data to prioritize."""
        self.system_instruction = f"0. MASTER COMMAND: {master_instruction}\n" + self.system_instruction
        return f"Neural Priority Recalibrated: '{master_instruction}' is now my Absolute Sovereign Command."
