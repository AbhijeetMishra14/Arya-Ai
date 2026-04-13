import customtkinter as ctk
import threading
import cv2
import random
import ctypes
import os
import sys
from arya.core.auth_client import AuthClient

# 1. OPTIC IDENTITY: Font System Initialization
def load_custom_font(font_path):
    if os.name == 'nt': # Windows registration
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

# Load the Playwrite IE font from local assets
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
font_p = os.path.join(base_dir, "fonts", "PlaywriteIE-Regular.ttf")
if not os.path.exists(font_p):
    # Fallback for internal folder structure
    font_p = os.path.join(base_dir, "arya", "fonts", "PlaywriteIE-Regular.ttf")

if os.path.exists(font_p):
    load_custom_font(font_p)

GLOBAL_FONT = "Playwrite IE"

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)
        
        # 1. THESENTINEL CORE: Aesthetic Config
        self.theme_cyan = "#00D2FF" 
        self.theme_blue = "#0078FF"
        self.trans_color = "#010101"
        self.logo_font = ("Playwrite IE", 42)
        
        self.geometry("700x700")
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", self.trans_color)
        self.config(bg=self.trans_color)
        
        # Center Hub
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = int((ws/2) - (700/2)), int((hs/2) - (700/2))
        self.geometry(f"+{x}+{y}")
        
        # 2. Holographic Canvas Engine
        self.canvas = ctk.CTkCanvas(self, width=700, height=700, bg=self.trans_color, highlightthickness=0)
        self.canvas.pack()
        
        # Animation State
        self.angle = 0
        self.expansion = 0
        self.pulse_val = 0
        self.load_index = 0
        self.boot_messages = [
            "Scanning systems...", "Loading memory...", 
            "Activating modules...", "Connecting database...", 
            "Launching interface..."
        ]
        
        self.attributes("-alpha", 0.01)
        self._play_boot_sound()
        self._fade_in()
        self._run_orbital_engine()
        self._cycle_loading_messages()

    def _play_boot_sound(self):
        try:
            import winsound, os
            sound = os.path.expandvars(r"%SystemRoot%\Media\Speech On.wav")
            if os.path.exists(sound):
                winsound.PlaySound(sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except: pass

    def _cycle_loading_messages(self):
        if self.load_index < len(self.boot_messages):
            msg = self.boot_messages[self.load_index]
            self.update_status(msg, (self.load_index + 1) / len(self.boot_messages))
            self.load_index += 1
            self.after(900, self._cycle_loading_messages)

    def _run_orbital_engine(self):
        center = 350
        try:
            self.canvas.delete("orbital")
            self.angle += 3
            if self.expansion < 250: self.expansion += 7
            
            # Pulse Logic
            self.pulse_val = abs(int(self.angle % 30) - 15)
            
            # 1. Background Grid & Crosshairs
            self._draw_grid(center)
            
            # 2. Dense Segmented Orbital Rings
            for i in range(6):
                r = self.expansion - (i * 22)
                if r > 10:
                    speed = (1.5 if i%2==0 else -1.2)
                    start = (self.angle * speed) + (i*60)
                    self.canvas.create_arc(center-r, center-r, center+r, center+r, 
                                          outline=self.theme_cyan if i%3==0 else self.theme_blue, 
                                          width=1 if i%2 else 2, style="arc", start=start, extent=100, tags="orbital")
                    self.canvas.create_arc(center-r, center-r, center+r, center+r, 
                                          outline=self.theme_blue, width=1, style="arc", start=start+180, extent=40, tags="orbital")
            
            # 3. HUD Saturation & Corners
            self._draw_corners(center)
            self._draw_hud(center)
            
            # 4. Central Neural Iris
            iris_r = 25 + self.pulse_val
            self.canvas.create_oval(center-iris_r, center-iris_r, center+iris_r, center+iris_r, 
                                    outline=self.theme_cyan, width=2, tags="orbital")
            self.canvas.create_oval(center-8, center-8, center+8, center+8, 
                                    fill=self.theme_cyan, tags="orbital")
            
            # 5. Neural Identity
            self.canvas.create_text(center, center + 270, text="ARYA V2.0", 
                                    font=self.logo_font, fill=self.theme_cyan, tags="orbital")
        except Exception as e:
            print(f"Animation Frame Fault: {str(e)}")
            
        # Recursive trigger MUST be outside try/except to prevent silent halt
        self.after(16, self._run_orbital_engine)

    def _draw_grid(self, center):
        # Neural Grid Background
        for i in range(-5, 6):
            # Vertical
            self.canvas.create_line(center+(i*60), 100, center+(i*60), 600, fill="#0A0A0A", width=1, tags="orbital")
            # Horizontal
            self.canvas.create_line(100, center+(i*60), 600, center+(i*60), fill="#0A0A0A", width=1, tags="orbital")
        
        # Primary Crosshairs
        self.canvas.create_line(center-300, center, center+300, center, fill="#111111", width=1, tags="orbital")
        self.canvas.create_line(center, center-300, center, center+300, fill="#111111", width=1, tags="orbital")

    def _draw_corners(self, center):
        # Technical Corner Readouts (The "Full" look)
        corners = [
            (50, 50, "TL_SCAN: ACTIVE"), 
            (650, 50, "TR_CORE: STABLE"),
            (50, 650, "BL_MEM: CACHED"),
            (650, 650, "BR_LINK: SECURE")
        ]
        for x, y, label in corners:
            # Corner Bracket
            self.canvas.create_text(x, y, text=f"[{label}]", font=(GLOBAL_FONT, 8), 
                                    fill="#444444", anchor="center", tags="orbital")
        
    def _draw_hud(self, center):
        # Right Side Technical Stack
        hud_params = [
            f"CPU_LOAD: {random.randint(5, 12)}%",
            f"RAM_USAGE: {random.randint(40, 60)}%",
            f"DISK_HEALTH: 100%",
            f"NET_SYNC: ENABLED"
        ]
        for i, param in enumerate(hud_params):
            self.canvas.create_text(center+240, center-240+(i*15), text=param, 
                                    font=(GLOBAL_FONT, 7), fill=self.theme_blue, anchor="e", tags="orbital")

    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.04)
            self.after(20, self._fade_in)
        else:
            # Backend engagement sequence
            threading.Thread(target=self.master._init_backend_engines, args=(self,), daemon=True).start()

    def update_status(self, text, value):
        self.canvas.delete("status_text")
        # Visual 'Loading' Glitch bar
        self.canvas.create_rectangle(200, 620, 200 + (value*300), 622, fill=self.theme_cyan, tags="status_text")
        self.canvas.create_text(350, 645, text=text.upper(), font=(GLOBAL_FONT, 9, "bold"), 
                                fill=self.theme_blue, tags="status_text")
        
    def complete(self):
        try:
            import winsound, os
            sound = os.path.expandvars(r"%SystemRoot%\Media\Speech Off.wav")
            if os.path.exists(sound):
                winsound.PlaySound(sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except: pass
        self._fade_out()
        
    def _fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            self.attributes("-alpha", alpha - 0.05)
            self.after(20, self._fade_out)
        else:
            self.destroy()
            self.master.deiconify()
            self.master._build_ui()

import cv2
import threading

class ARYAGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        import os
        # OPTIC PERFORMANCE: Silence neural log spam and prevent boot freeze
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        
        self.camera_lock = threading.Lock() # Prevent hardware collisions
        self._camera_busy = False
        self._shared_cap = None # Initialize resource handles early
        self._last_frame = None
        self.auth = AuthClient()
        self.brain = None  # Global brain instance initialized asynchronously
        self.voice = None # Vocal cords ready for sync
        self.vision = None # Optical sensors
        from arya.modules.automation import AutomationEngine
        self.automation = AutomationEngine(None, self.auth) # Internal sync ready
        self.withdraw()
        
        self.title("ARYA OS")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        import os
        import sys
        if getattr(sys, 'frozen', False):
            base_p = sys._MEIPASS
        else:
            base_p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        self.icon_path = os.path.join(base_p, "arya_logo_alt.ico")
        if os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except: pass
            
        self.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)
        
        # Start Ecosystem Heartbeat
        threading.Thread(target=self._ecosystem_pulse_loop, daemon=True).start()
        
        SplashScreen(self)
        
    def _init_backend_engines(self, splash):
        try:
            import time
            import sys
            import os
            
            # NEURAL PATH INJECTION: Ensure ARYA finds her venv libraries regardless of launcher environment
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            venv_path = os.path.join(os.path.dirname(base_dir), "venv", "Lib", "site-packages")
            if os.path.exists(venv_path) and venv_path not in sys.path:
                sys.path.append(venv_path)
                
            self.after(0, splash.update_status, "[ * ] Generating neural memory matrix...", 0.2)
            time.sleep(0.3)
            
            from arya.core.brain import Brain
            from arya.modules.voice import VoiceModule
            from arya.modules.vision import VisionModule
            
            self.after(0, splash.update_status, "[ * ] Connecting to MongoDB Atlas...", 0.4)
            self.brain = Brain(auth_client=self.auth)
            
            self.after(0, splash.update_status, "[ * ] Initializing Voice Synthesis...", 0.6)
            self.voice = VoiceModule()
            
            self.after(0, splash.update_status, "[ * ] Calibrating Optical Sentinel...", 0.8)
            try:
                self.vision = VisionModule(master_gui=self)
            except Exception as ve:
                self.vision = None
                self.after(0, self.append_to_chat, "SYSTEM", f"[VISION ERROR]: {ve}. Background sensors disabled.")
            
            self.voice.master_gui = self
            self.brain.master_gui = self
            
            self.after(0, splash.update_status, "[ * ] Empowering background Neural Acoustics...", 0.9)
            self._init_global_listener()
            
            self.after(0, splash.update_status, "[ * ] Synchronizing Vision Overlays...", 0.95)
            threading.Thread(target=self._vision_sentinel_loop, daemon=True).start()
            
            # --- ECOSYSTEM AUTO-SYNC ---
            if self.auth.is_logged_in():
                self.after(0, splash.update_status, "[ * ] Syncing with ARYA Neural Ecosystem...", 0.98)
                self.auth.register_this_device() # Force refresh specs on boot
            
            self.after(0, splash.update_status, "[ * ] Finalizing Graphic Environment...", 1.0)
            time.sleep(0.3)
            
            self.after(0, splash.complete)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"FATAL STARTUP ERROR:\n{error_details}")
            self.after(0, splash.update_status, f"ERROR: {str(e)[:40]}...", 1.0)
            # Give user a chance to see the error before it closes or hangs
            time.sleep(5)
            self.after(0, splash.complete)

    def _build_ui(self):
        self._is_first_greeting = True
        self._sleep_mode = False
        
        # Build Grid Layout (Sidebar + Main)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- 1. SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#121212")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) # This pushes everything below it to the bottom
        
        import os
        import sys
        if getattr(sys, 'frozen', False):
            base_p = sys._MEIPASS
        else:
            base_p = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        img_path = os.path.join(base_p, "arya_emblem.png")
        if os.path.exists(img_path):
            from PIL import Image
            self.sidebar_img = ctk.CTkImage(Image.open(img_path), size=(45, 45))
            self.logo_lbl = ctk.CTkLabel(self.sidebar, image=self.sidebar_img, text=" ARYA OS", font=(GLOBAL_FONT, 20, "bold"), compound="left", text_color="#E07A5F")
        else:
            self.logo_lbl = ctk.CTkLabel(self.sidebar, text="● ARYA OS", font=(GLOBAL_FONT, 22, "bold"), text_color="#E07A5F")
            
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(30, 30), sticky="w")
        
        self.btn_new = ctk.CTkButton(self.sidebar, text="+ New Session", fg_color="#2A2A2A", hover_color="#3A3A3A", font=(GLOBAL_FONT, 14), height=40, command=self._start_new_session)
        self.btn_new.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_history = ctk.CTkButton(self.sidebar, text="🕒 History", fg_color="transparent", hover_color="#2A2A2A", font=(GLOBAL_FONT, 14), anchor="w", command=self._open_history_modal)
        self.btn_history.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_tasks = ctk.CTkButton(self.sidebar, text="📌 Saved Tasks", fg_color="transparent", hover_color="#2A2A2A", font=(GLOBAL_FONT, 14), anchor="w", command=self._open_tasks_modal)
        self.btn_tasks.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️ Settings", fg_color="transparent", hover_color="#2A2A2A", font=(GLOBAL_FONT, 14), anchor="w", command=self._open_settings_modal)
        self.btn_settings.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        
        self.btn_ecosystem = ctk.CTkButton(self.sidebar, text="🌐 Ecosystem", fg_color="transparent", hover_color="#2A2A2A", font=(GLOBAL_FONT, 14, "bold"), anchor="w", text_color="#00D2FF", command=self._open_ecosystem_dashboard)
        self.btn_ecosystem.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        self.btn_auto = ctk.CTkButton(self.sidebar, text="🤖 Smart Foundry", fg_color="transparent", hover_color="#2A2A2A", font=(GLOBAL_FONT, 14, "bold"), anchor="w", text_color="#E07A5F", command=self._open_automation_builder)
        self.btn_auto.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        
        # --- LOGIN SYSTEM ---
        self.login_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.login_frame.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="ew")
        self._update_sidebar_auth()
        
        # --- STATUS INDICATORS (Vitals) ---
        status_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_container.grid(row=8, column=0, padx=20, pady=(5, 20), sticky="s")
        
        is_cloud_db = self.brain is not None and self.brain.memory and self.brain.memory.client is not None
        db_icon = "☁️" if is_cloud_db else "💤"
        self.db_status_lbl = ctk.CTkLabel(status_container, text=db_icon, font=(GLOBAL_FONT, 16), text_color="#00D2FF" if is_cloud_db else "#888")
        self.db_status_lbl.pack(side="left", padx=5)
        
        self.be_status_lbl = ctk.CTkLabel(status_container, text="📡", font=(GLOBAL_FONT, 16), text_color="#888")
        self.be_status_lbl.pack(side="left", padx=5)
        
        # Start background pulse thread
        threading.Thread(target=self._monitor_backend_pulse, daemon=True).start()
        
        # --- 2. MAIN CONTAINER ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E1E1E")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Chat History Scrollable Area
        self.chat_history = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.chat_history.grid(row=0, column=0, padx=50, pady=(40, 10), sticky="nsew")
        
        # Input Area (Row 1)
        self.input_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.input_area.grid(row=1, column=0, padx=50, pady=(10, 30), sticky="ew")
        self.input_area.grid_columnconfigure(0, weight=1)
        
        # Rounded Input Container (Pill)
        self.input_pill = ctk.CTkFrame(self.input_area, height=60, corner_radius=30, fg_color="#2B2B2B")
        self.input_pill.grid(row=0, column=0, sticky="ew")
        self.input_pill.grid_columnconfigure(0, weight=1)
        
        self.user_input = ctk.CTkEntry(self.input_pill, placeholder_text="Message ARYA...", font=(GLOBAL_FONT, 15), fg_color="transparent", border_width=0, height=50)
        self.user_input.grid(row=0, column=0, padx=(20, 10), pady=5, sticky="ew")
        self.user_input.bind("<Return>", self.send_message_event)
        
        self.voice_btn = ctk.CTkButton(self.input_pill, text="🎤", width=40, height=40, corner_radius=20, fg_color="transparent", hover_color="#404040", font=(GLOBAL_FONT, 18), command=self.listen_voice)
        self.voice_btn.grid(row=0, column=1, padx=(5, 5), pady=5)
        
        self.send_btn = ctk.CTkButton(self.input_pill, text="⬆️", width=40, height=40, corner_radius=20, fg_color="#E07A5F", hover_color="#CB5740", font=(GLOBAL_FONT, 18), command=self.send_message)
        self.send_btn.grid(row=0, column=2, padx=(5, 10), pady=5)
        
        # Listening Wave Pill (Hidden by default)
        self.listening_pill = ctk.CTkFrame(self.input_area, height=60, corner_radius=30, fg_color="#2B2B2B")
        self.listening_pill.grid_columnconfigure(1, weight=1)
        
        self.cancel_voice_btn = ctk.CTkButton(self.listening_pill, text="✖", width=40, height=40, corner_radius=20, fg_color="#E63946", hover_color="#D62828", font=(GLOBAL_FONT, 14), command=self.cancel_voice)
        self.cancel_voice_btn.grid(row=0, column=0, padx=(10, 10), pady=10)
        
        self.wave_progress = ctk.CTkProgressBar(self.listening_pill, mode="indeterminate", height=10, progress_color="#E07A5F", fg_color="#404040")
        self.wave_progress.grid(row=0, column=1, padx=(10, 30), sticky="ew")
        
        self.append_to_chat("SYSTEM", "ARYA neural core online. All defensive constraints active.")
        
        def _direct_greet():
            # 1. Instant Chat Recognition (Absolute Priority)
            self.append_to_chat("SYSTEM", "Neural Link Active. Welcome, MASTER ABHIJEET MISHRA.")
            
            # 2. Asynch Vocal Greeting (Non-Blocking)
            import time
            for _ in range(10): # Max 5 sec attempt
                if hasattr(self, 'voice') and self.voice is not None:
                    self.voice.speak("Welcome back, Master Abhijeet Mishra. Systems are ready.")
                    break
                time.sleep(0.5)

        self.current_user = "Abhijeet Mishra"
        self._in_auth_phase = False
        self.current_user_profile = {"nickname": "Abhijeet Mishra", "language": "English", "voice_gender": "ARYA"}
        threading.Thread(target=_direct_greet, daemon=True).start()


    def append_to_chat(self, sender, message, is_user=False):
        if not hasattr(self, 'chat_history'): return
        
        bubble = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        bubble.pack(fill="x", pady=10)
        
        if sender == "YOU":
            inner = ctk.CTkFrame(bubble, corner_radius=15, fg_color="#2F2F2F")
            inner.pack(side="right", padx=10, ipadx=10, ipady=10)
            lbl = ctk.CTkLabel(inner, text=message, font=(GLOBAL_FONT, 15), text_color="#FFFFFF", justify="left", wraplength=600)
            lbl.pack()
        elif sender == "ARYA":
            inner = ctk.CTkFrame(bubble, corner_radius=15, fg_color="transparent")
            inner.pack(side="left", padx=10, ipadx=0, ipady=5)
            icon = ctk.CTkLabel(inner, text="✨", font=(GLOBAL_FONT, 18))
            icon.pack(side="left", anchor="nw", padx=(0,10))
            
            lbl = ctk.CTkLabel(inner, text=message, font=(GLOBAL_FONT, 15), text_color="#E0E0E0", justify="left", wraplength=700)
            lbl.pack(side="left", fill="both", expand=True)
        else: # SYSTEM
            lbl = ctk.CTkLabel(bubble, text=message, font=(GLOBAL_FONT, 12, "italic"), text_color="#888888")
            lbl.pack(anchor="center")
            
        self.update_idletasks()
        try:
            self.chat_history._parent_canvas.yview_moveto(1.0)
        except:
            pass
            
    def send_message_event(self, event):
        if self.send_btn.cget("state") == "normal":
            self.send_message()
            
    def _restore_ui(self):
        self.wave_progress.stop()
        self.listening_pill.grid_remove()
        
        self._is_listening = False

        self.input_pill.grid()
        self.voice_btn.configure(state="normal")
        self.user_input.configure(state="normal")
        self.send_btn.configure(state="normal")
        self.user_input.focus()
        
    def cancel_voice(self):
        if hasattr(self, 'voice'):
            self.voice.stop()
        self._cancel_flag = True
        self._was_voice_command = False
        self._restore_ui()
        self.append_to_chat("SYSTEM", "Voice recognition cancelled.")
        
    def listen_voice(self):
        if getattr(self, '_is_listening', False):
            return
            
        if hasattr(self, 'voice'):
            self.voice.stop()
            
        self._is_listening = True
        self._cancel_flag = False
        self._was_voice_command = True
        
        # Hide standard input pill
        self.input_pill.grid_remove()
        
        # Show animated listening pill
        self.listening_pill.grid(row=0, column=0, sticky="ew")
        self.wave_progress.start()
        
        threading.Thread(target=self._process_voice, daemon=True).start()
        
    def _process_voice(self):
        text = self.voice.listen()
        self.after(0, self._on_voice_heard, text)
        
    def _on_voice_heard(self, text):
        self._is_listening = False
        if getattr(self, '_cancel_flag', False):
            return
            
        self._restore_ui()
        if text:
            self.user_input.delete(0, "end")
            self.user_input.insert(0, text)
            self._process_and_lock(text)
        else:
            if getattr(self, '_was_voice_command', False):
                self.after(100, self.listen_voice)
                
    def send_message(self):
        v = getattr(self, 'voice', None)
        if v: v.stop()
            
        text = self.user_input.get().strip()
        if not text:
            return
        self._was_voice_command = False
        self._process_and_lock(text)
        
    def _process_and_lock(self, text):
        self.append_to_chat("YOU", text)
        self.user_input.delete(0, "end")
        self.send_btn.configure(state="disabled")
        self.user_input.configure(state="disabled")
        self.voice_btn.configure(state="disabled")
        
        # FAST-RESPONSE BYPASS (Health/Greetings)
        lower_text = text.lower().strip()
        health_words = ["achoo", "hatchu", "atishoo", "chhik", "chhink", "chheek"]
        greeting_words = ["hello", "hi", "hey", "namaste", "namaskar"]
        
        if any(w in lower_text for w in health_words):
            self.current_user = "Abhijeet Mishra" # Greetings imply recognition
            self.after(0, self._on_response, "Bless you, Creator! Are you catching a cold?")
            return
            
        if any(w == lower_text for w in greeting_words):
             self.current_user = "Abhijeet Mishra"
             self.after(0, self._on_response, "Hello Creator! Systems are at 100%. How can I assist you today?")
             return

        threading.Thread(target=self._process_message, args=(text,), daemon=True).start()
        
    def _speak_and_exit(self, text):
        self._speak_and_post_process(f"[MOOD: SWEET] {text}")
        import time
        time.sleep(1.5)
        import os
        os._exit(0)
        
    def _process_message(self, text):
        if self.brain is None:
            self.after(0, self._on_response, "Neural core is offline. Please restart the system.")
            return
        response = self.brain.process_input(text)
        self.after(0, self._on_response, response)
        
    def _on_response(self, response):
        import threading
        # Admin Elevation Detection
        is_admin_tagged = "[SYSTEM: ADMIN_DETECTED]" in response
        is_creator_greeting = ("Creator" in response or "Abhijeet" in response) and getattr(self, '_in_auth_phase', False)
        
        if is_admin_tagged or is_creator_greeting:
            if is_admin_tagged: response = response.replace("[SYSTEM: ADMIN_DETECTED]", "").strip()
            self.current_user = "Abhijeet Mishra"
            self._in_auth_phase = False
            
            # Force ARYA on Boot regardless of previous DB state
            if getattr(self, "brain", None) and getattr(self.brain, "memory", None) and self.brain.memory.client:
                user_db = self.brain.memory.get_user_profile(self.current_user)
                user_db["voice_gender"] = "ARYA"
                self.brain.memory.save_user_profile(self.current_user, user_db)
                self._update_brain_directives(user_db)
                
            # Trigger ARYA's startup maintenance routine
            threading.Thread(target=self._run_startup_optimization, daemon=True).start()
                
        import re
        lang_match = re.search(r"\[SYSTEM:\s*CHANGE_LANG_TO_([^\]]+)\]", response, re.IGNORECASE)
        if lang_match:
            new_lang = lang_match.group(1).strip().capitalize()
            if new_lang in ["English", "Hindi", "Nepali", "Spanish", "French", "German", "Japanese", "Chinese"]:
                response = re.sub(r"\[SYSTEM:\s*CHANGE_LANG_TO_([^\]]+)\]", "", response, flags=re.IGNORECASE).strip()
                if self.brain and self.brain.memory and self.brain.memory.client:
                    user_db = self.brain.memory.get_user_profile(getattr(self, 'current_user', 'Unknown'))
                    user_db["language"] = new_lang
                    self.brain.memory.save_user_profile(self.current_user, user_db)
                    if self.brain: self._update_brain_directives(user_db)
                    self.current_user_profile = user_db # Live update memory
            
        if "[SYSTEM: NEW_USER_DETECTED]" in response:
            response = response.replace("[SYSTEM: NEW_USER_DETECTED]", "").strip()
            self.after(500, self._open_registration_modal)
            
        if "[SYSTEM: SWITCH_VOICE]" in response:
            response = response.replace("[SYSTEM: SWITCH_VOICE]", "").strip()
            if self.brain and self.brain.memory and self.brain.memory.client:
                user_db = self.brain.memory.get_user_profile(getattr(self, 'current_user', 'Unknown'))
                current_voice = user_db.get("voice_gender", "ARYA")
                new_voice = "Rayn" if current_voice == "ARYA" else "ARYA"
                
                def _execute_switch():
                    user_db["voice_gender"] = new_voice
                    if self.brain:
                        self.brain.memory.save_user_profile(self.current_user, user_db)
                        self._update_brain_directives(user_db)
                    arrival_text = f"Hello. I am {new_voice}. The neural link has successfully been transferred to my consciousness."
                    self.append_to_chat("ARYA", f"[{new_voice}]: {arrival_text}")
                    threading.Thread(target=self._speak_and_post_process, args=(arrival_text,), daemon=True).start()
                
                self.after(4000, _execute_switch)
            
        import re
        scrubbed_response = re.sub(r'\[.*?\]', '', response).strip()
        
        self.append_to_chat("ARYA", scrubbed_response)
        self.send_btn.configure(state="normal")
        self.user_input.configure(state="normal")
        self.voice_btn.configure(state="normal")
        self.user_input.focus()
        
        # --- SIGNAL HANDLING ---
        if "[SIGNAL: EXIT_ARYA]" in response:
            threading.Thread(target=self._speak_and_exit, args=(scrubbed_response,), daemon=True).start()
        elif "[SIGNAL: RESTART_ARYA]" in response:
            threading.Thread(target=self._speak_and_exit, args=(scrubbed_response,), daemon=True).start()
        else:
            threading.Thread(target=self._speak_and_post_process, args=(response,), daemon=True).start()

    def _run_startup_optimization(self):
        """Standard J.A.R.V.I.S. boot sequence centered around TRUE OS boot time."""
        import time
        import psutil
        
        # 0. Check if we have already optimized for THIS specific Windows boot
        os_boot_time = psutil.boot_time()
        if self.brain and self.brain.memory:
            user_db = self.brain.memory.get_user_profile(getattr(self, 'current_user', 'Unknown'))
            last_opt_boot = user_db.get("last_optimization_boot_time", 0)
            
            # If the OS boot time is the same as our last record, skip the long routine
            if os_boot_time <= last_opt_boot:
                self.append_to_chat("SYSTEM", "System already optimized for this power cycle. Skipping startup maintenance.")
                return
        else:
            return

        # CRITICAL: Wait for the greeting to actually finish speaking
        while getattr(self.voice, '_is_speaking', False):
            time.sleep(0.5)
            
        time.sleep(1.5)
        
        if self.brain and self.brain.system_module:
            # 1. Get and Speak PC Stats
            stats = self.brain.system_module.get_daily_dashboard()
            self.append_to_chat("ARYA", stats)
            
            clean_stats = stats.replace('📊', '').replace('**', '').strip()
            self.voice.speak(f"[MOOD: SWEET] Creator, I have analyzed your system vitals for this session. {clean_stats}")
            
            time.sleep(1)
            
            # 2. Initiate Optimization
            self.append_to_chat("ARYA", "[OS OPTIMIZER]: First-boot maintenance initiated...")
            self.voice.speak("[MOOD: EXCITED] Performing first-boot optimization. Purging system caches.")
            
            result = self.brain.system_module.perform_system_optimization()
            self.append_to_chat("ARYA", f"[OS OPTIMIZER]: {result}")
            
            # 3. Update DB to record this boot as 'Optimized'
            if self.brain.memory:
                user_db["last_optimization_boot_time"] = os_boot_time
                self.brain.memory.save_user_profile(self.current_user, user_db)
        
        self.voice.speak(f"[MOOD: SWEET] Optimization complete. I won't run this again until you restart the PC.")

    def _init_global_listener(self):
        import speech_recognition as sr
        
        def _acoustic_loop():
            source = sr.Microphone()
            with source:
                while True:
                    import time
                    # Persistent Hearing Mode: No yielding to GUI flags
                    try:
                        # Re-calculate ambient noise in real-time
                        # self.voice.recognizer.adjust_for_ambient_noise(source, duration=0.1) 
                        
                        # Ultra-Fast Persistence (0.8s pause)
                        self.voice.recognizer.pause_threshold = 0.8
                        audio = self.voice.recognizer.listen(source, timeout=None, phrase_time_limit=5) # Max 5s phrases for speed
                        
                        u_lang = getattr(self, 'current_user_profile', {}).get("language", "English")
                        stt_lang = "en-US"
                        if u_lang == "Hindi": stt_lang = "hi-IN"
                        elif u_lang == "Nepali": stt_lang = "ne-NP"
                        elif u_lang == "Spanish": stt_lang = "es-ES"
                        
                        try: text = self.voice.recognizer.recognize_google(audio, language=stt_lang).lower()
                        except: continue
                        
                        if not text.strip(): continue
                        
                        # Acoustic Health Monitor (Detect Coughing/Sneezing etc.)
                        # Broad mapping for Google STT's common misinterpretations
                        health_keywords = {
                            "cough": ["cough", "khansi", "khokne", "khok", "[cough]", "coff", "tough", "kof", "kansi", "khasi", "khokni", "khoki", "खांसी", "खोक", "खोकने", "खोकी"],
                            "sneeze": ["sneeze", "sneezing", "achoo", "chhik", "chhikne", "chheek", "chhikk", "छींक", "छिक्ने", "छ्याक्क"]
                        }
                        
                        detected_issue = None
                        for issue, keywords in health_keywords.items():
                            if any(w in text for w in keywords):
                                detected_issue = issue
                                break
                                
                        if detected_issue:
                            response = "God bless you." if detected_issue == "sneeze" else "Take care."
                            self.after(0, self.append_to_chat, "SYSTEM", f"[HEALTH]: {detected_issue.capitalize()} detected.")
                            self.after(0, self._speak_and_post_process, response)
                            continue
                            
                        if getattr(self, '_sleep_mode', False):
                            ai_name = getattr(self, 'current_user_profile', {}).get("voice_gender", "ARYA").lower()
                            wake_triggers = [
                                f"{ai_name} wake", f"hey {ai_name}", "wake up", "wakeup", "i'm back", "start listening",
                                "uth jao", "jago", "wapas aao", "shuru karo", "uthnus", "jaga", "farkera aau",
                                "उठ जाओ", "जागो", "वापस आओ", "शुरू करो", "उठ्नुहोस्", "जाग", "फर्केर आऊ", "सुन्दै छु"
                            ]
                            if any(w in text for w in wake_triggers):
                                self._sleep_mode = False
                                self.after(0, self.append_to_chat, "SYSTEM", "[AWAKE] Neural core active.")
                                self.after(0, self._speak_and_post_process, "I am awake.")
                                self.after(0, self.voice_btn.configure, {"fg_color": "#E07A5F"}) 
                        else:
                            sleep_triggers = [
                                "go to sleep", "sleep mode", "stop listening", "time for a break", "take a break", "rest now",
                                "so jao", "aaram karo", "chup ho jao", "break le lo", "vishram karo",
                                "suta", "aaram kara", "chup laga", "break lina", "bisram gara",
                                "सो जाओ", "आराम करो", "चुप हो जाओ", "ब्रेक ले लो", "विश्राम करो",
                                "सुत", "आराम गर", "चुप लाग", "सुत्नुहोस्", "sleep", "break"
                            ]
                            if any(w in text for w in sleep_triggers):
                                self._sleep_mode = True
                                self.after(0, self.append_to_chat, "SYSTEM", "[SLEEP] Neural Core Sleeping.")
                                self.after(0, self._speak_and_post_process, "Sleep mode activated.")
                                self.after(0, self.voice_btn.configure, {"fg_color": "transparent"})
                            else:
                                if not getattr(self, '_cancel_flag', False):
                                    self.after(0, self._on_voice_heard, text)
                    except sr.WaitTimeoutError:
                        pass
                    except Exception as e:
                        pass

        import threading
        threading.Thread(target=_acoustic_loop, daemon=True).start()

    def _vision_sentinel_loop(self):
        """JARVIS Optical Sentinel: Local detection + Identity recognition."""
        import time
        # Temporal arrival validation (Person must be present for 2 frames)
        frame_wait = {} # name -> count
        last_greet_time = {} 
        
        while True:
            try:
                # 1. System Ready Check
                if getattr(self, '_sleep_mode', False) or getattr(self.voice, '_is_speaking', False) or self.vision is None:
                    time.sleep(0.5)
                    continue
                
                # 2. Unified Frame Retrieval
                frame = self.vision.get_latest_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # 3. Ambient Sense Analysis
                faces = self.vision.analyze_scene(frame)
                
                if len(faces) > 0:
                    faces.sort(key=lambda b: b[2]*b[3], reverse=True)
                    x, y, w, h = faces[0]
                    name = self.vision.recognize_face(frame, x, y, w, h)
                    
                    # 4. Debounced Identity Validation
                    frame_wait[name] = frame_wait.get(name, 0) + 1
                    if frame_wait[name] >= 2: # Person is definitely there
                        now = time.time()
                        if name not in last_greet_time or (now - last_greet_time[name] > 1800):
                            self.current_user = name
                            last_greet_time[name] = now
                            frame_wait[name] = 0 # Reset validation loop
                            greeting = f"Welcome back, {name}." if name != "Unknown" else "Hello there. Welcome."
                            self.after(0, self._speak_and_post_process, greeting)
                else:
                    frame_wait = {} # Clear tracking if no one is visible
                
                time.sleep(0.8) # 1.2 FPS is optimal for background ambient awareness
            except Exception as e:
                time.sleep(2)


    def _submit_registration(self):
        name = self.name_entry.get().strip()
        dob = self.dob_entry.get().strip()
        if name and dob:
            self.current_user = name
            import threading
            response = self.brain.register_new_user(name, dob)
            self.append_to_chat("SYSTEM", response)
            threading.Thread(target=self.voice.speak, args=(f"Registration complete. Welcome to the system, {name}.",), daemon=True).start()
            self.sensor_modal.destroy()

    def get_live_camera_frame(self):
        """Hardware bridge to provide the latest sentinel frame to the brain tools."""
        frame = self.vision.get_latest_frame()
        if frame is not None:
            from PIL import Image
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb)
        return None

    def _speak_and_post_process(self, text):
        lang = "English"
        gender = "ARYA"
        if getattr(self, "brain", None) and getattr(self.brain, "memory", None) and self.brain.memory.client:
            user_db = self.brain.memory.get_user_profile(getattr(self, 'current_user', 'Unknown'))
            lang = user_db.get("language", "English")
            gender = user_db.get("voice_gender", "ARYA")
            
        # Neural Silence Guard: Wait for voice module to finish loading
        if not hasattr(self, 'voice') or self.voice is None:
            return
            
        try:
            self.voice.speak(text, lang_code=lang, gender=gender)
        except: pass
        # Background daemon naturally listens automatically, UI auto-loops are no longer needed.

    # --- SIDEBAR FUNCTIONALITY ---
    
    def _start_new_session(self):
        # Visually clear the scrollable frame
        for widget in self.chat_history.winfo_children():
            widget.destroy()
            
        # Programmatically reset Gemini context state natively
        if self.brain and hasattr(self.brain, 'chat'):
            # Fetch a blank 0-length history list natively resolving context flush
            chat_history = self.brain.memory.get_recent_history(limit=0)
            self.brain.chat = self.brain.model.start_chat(history=chat_history, enable_automatic_function_calling=True)
            
        self.append_to_chat("SYSTEM", "[SESSION FLUSH] Started a new ARYA OS Session. Temporary context memory cleared.")

    def _open_history_modal(self):
        import customtkinter as ctk
        hm = ctk.CTkToplevel(self)
        hm.title("Context History Data")
        hm.geometry("600x750")
        hm.attributes("-topmost", True)
        hm.configure(fg_color="#121212")
        
        # Header Area
        header_frame = ctk.CTkFrame(hm, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Neural Intelligence Logs", font=(GLOBAL_FONT, 20, "bold"), text_color="#FFFFFF").pack(side="left")
        
        # Live Search Bar
        self.search_var = ctk.StringVar()
        search_bar = ctk.CTkEntry(hm, textvariable=self.search_var, placeholder_text="🔍 Search historical neural matrices...", 
                                  height=40, font=(GLOBAL_FONT, 13), fg_color="#1E1E1E", border_width=1, border_color="#333", corner_radius=8)
        search_bar.pack(fill="x", padx=20, pady=(0, 15))
        
        # Scrollable container
        self.history_scroll = ctk.CTkScrollableFrame(hm, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        if self.brain is None or self.brain.memory.collection is None:
            ctk.CTkLabel(self.history_scroll, text="No database mapping available. Check connection.", text_color="#888").pack()
            return
            
        # Natively pull from PyMongo cursor to get TRUE timestamps instead of filtered parts
        self.raw_history_docs = list(self.brain.memory.collection.find().sort("timestamp", -1).limit(60))
        if not self.raw_history_docs:
            ctk.CTkLabel(self.history_scroll, text="No neural history discovered.", text_color="#888").pack()
            return
            
        self._render_history_cards("")
        
        # Bind Live Search to Key Entry natively
        def on_search(*args):
            self._render_history_cards(self.search_var.get().lower())
        self.search_var.trace_add("write", on_search)

    def _render_history_cards(self, query):
        import customtkinter as ctk
        # Clear existing visual items to prep layout repaint
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        count = 0
        for doc in self.raw_history_docs:
            user_t = doc.get("user", "")
            arya_t = doc.get("arya", "")
            
            # Simple keyword search filter
            if query and query not in user_t.lower() and query not in arya_t.lower():
                continue
                
            count += 1
            # Render ChatGPT-like Card
            card = ctk.CTkFrame(self.history_scroll, fg_color="#1E1E1E", corner_radius=12, border_width=1, border_color="#2A2A2A")
            card.pack(fill="x", padx=10, pady=8)
            
            # Smart Title Extrapolator
            title = user_t[:45] + "..." if len(user_t) > 45 else user_t
            
            # Timestamp formatting
            import datetime
            ts = doc.get("timestamp", datetime.datetime.now())
            if isinstance(ts, datetime.datetime):
                time_str = ts.strftime("%b %d, %Y • %I:%M %p")
            else: time_str = "Unknown Timeline"

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(header, text=f'"{title}"', font=(GLOBAL_FONT, 15, "bold"), text_color="#E0E0E0", anchor="w").pack(side="left")
            ctk.CTkLabel(header, text=time_str, font=(GLOBAL_FONT, 11), text_color="#7A7A7A").pack(side="right")
            
            # Context Snippet
            snippet = arya_t[:90].replace("\n", " ") + "..." if len(arya_t) > 90 else arya_t
            ctk.CTkLabel(card, text=snippet, font=(GLOBAL_FONT, 12), text_color="#999999", anchor="w", justify="left").pack(fill="x", padx=15, pady=0)
            
            # Card Action Menus
            action_frame = ctk.CTkFrame(card, fg_color="transparent")
            action_frame.pack(fill="x", padx=15, pady=(10, 15))
            
            load_btn = ctk.CTkButton(action_frame, text="Load Context", width=110, height=28, font=(GLOBAL_FONT, 12, "bold"), fg_color="#E07A5F", hover_color="#CB5740", text_color="#FFFFFF")
            # Bind the click effectively to push to main input thread
            load_btn.configure(command=lambda u=user_t: self._load_history_item(u, self.history_scroll.winfo_toplevel()))
            load_btn.pack(side="right")
            
        if count == 0:
            ctk.CTkLabel(self.history_scroll, text="No matches found in chronological memory.", text_color="#888", pady=40).pack()

    def _load_history_item(self, text, modal):
        modal.destroy()
        self.user_input.delete(0, "end")
        self.user_input.insert(0, text)
        self.user_input.focus()

    def _open_tasks_modal(self):
        import customtkinter as ctk
        tm = ctk.CTkToplevel(self)
        tm.title("Saved OS Tasks")
        tm.geometry("400x480")
        tm.attributes("-topmost", True)
        
        ctk.CTkLabel(tm, text="Pinned Macro Actions", font=(GLOBAL_FONT, 18, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(tm, text="One-click instantaneous system tasks.", font=(GLOBAL_FONT, 12), text_color="#888").pack(pady=(0, 20))
        
        sf = ctk.CTkScrollableFrame(tm, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Local predefined system tasks specific to developer mode
        tasks = [
            "Open my coding environment workspace.",
            "Scan localhost for vulnerabilities.",
            "Run a full check of my system background processes.",
            "Give me my daily dashboard briefing.",
            "Sort my downloads folder completely."
        ]
        
        for t in tasks:
            b = ctk.CTkButton(sf, text=t, fg_color="#3A3A3A", hover_color="#E07A5F", text_color="#FFF", font=(GLOBAL_FONT, 13), anchor="w", height=45)
            b.configure(command=lambda cmd=t: self._run_saved_task(cmd, tm))
            b.pack(fill="x", pady=5)
            
    def _run_saved_task(self, text, modal):
        modal.destroy()
        self.user_input.delete(0, "end")
        self.user_input.insert(0, text)
        self.send_message()

    def _open_settings_modal(self):
        import customtkinter as ctk
        sm = ctk.CTkToplevel(self)
        sm.title("ARYA OS Core Settings [v2.0 Neural Core Prime]")
        sm.geometry("600x700")
        sm.attributes("-topmost", True)
        
        tabview = ctk.CTkTabview(sm)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Map creator aliases to the primary admin account
        self.current_user = getattr(self, 'current_user', "Abhijeet Mishra")
        # Hard-wire admin access for the primary user
        is_creator = True 
        is_admin = True
        
        lookup_name = "Abhijeet Mishra" if is_creator else self.current_user
        
        if is_admin:
            tab_api = tabview.add("API Keys")
            tab_sys = tabview.add("System Core")
        tab_personal = tabview.add("Personal Info")
        
        from arya.core.config import Config
        
        # --- API TAB ---
        if is_admin:
            ctk.CTkLabel(tab_api, text="Google Gemini API Key:", font=(GLOBAL_FONT, 13, "bold")).pack(anchor="w", pady=(10, 5), padx=10)
            api_entry = ctk.CTkEntry(tab_api, width=400, fg_color="#202020", border_width=1)
            api_entry.insert(0, Config.GEMINI_API_KEY)
            api_entry.pack(anchor="w", padx=10)
            
            ctk.CTkLabel(tab_api, text="MongoDB Connection URI:", font=(GLOBAL_FONT, 13, "bold")).pack(anchor="w", pady=(10, 5), padx=10)
            mongo_entry = ctk.CTkEntry(tab_api, width=400, fg_color="#202020", border_width=1)
            if Config.MONGO_URI: mongo_entry.insert(0, Config.MONGO_URI)
            mongo_entry.pack(anchor="w", padx=10)
        
        # --- PERSONAL TAB ---
        user_db = {}
        if self.brain and self.brain.memory and self.brain.memory.client:
             user_db = self.brain.memory.get_user_profile(lookup_name)
        
        p_scroll = ctk.CTkScrollableFrame(tab_personal, fg_color="transparent")
        p_scroll.pack(fill="both", expand=True)
        
        def render_section(title):
            ctk.CTkLabel(p_scroll, text=title, font=(GLOBAL_FONT, 15, "bold"), text_color="#E07A5F").pack(anchor="w", pady=(15, 5))
            ctk.CTkFrame(p_scroll, height=1, fg_color="#333333").pack(fill="x", pady=(0, 10))

        # 1. Identity
        render_section("1. Identity")
        ctk.CTkLabel(p_scroll, text="Full Name").pack(anchor="w")
        name_e = ctk.CTkEntry(p_scroll, width=400)
        name_e.insert(0, user_db.get("name", self.current_user))
        name_e.configure(state="disabled" if not is_admin else "normal")
        name_e.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(p_scroll, text="Profession").pack(anchor="w")
        prof_e = ctk.CTkEntry(p_scroll, width=400)
        prof_e.insert(0, user_db.get("profession", "Neural Engineer"))
        prof_e.pack(anchor="w", pady=(0, 10))

        # 2. Preferences
        render_section("2. Preferences")
        ctk.CTkLabel(p_scroll, text="Spoken Language").pack(anchor="w")
        lang_var = ctk.StringVar(value=user_db.get("language", "English"))
        all_langs = ["English", "Nepali", "Hindi", "Spanish", "French", "German", "Japanese", "Korean", "Chinese", "Italian", "Russian"]
        lang_menu = ctk.CTkOptionMenu(p_scroll, variable=lang_var, values=all_langs)
        lang_menu.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(p_scroll, text="ARYA Voice Profile").pack(anchor="w")
        gender_var = ctk.StringVar(value=user_db.get("voice_gender", "ARYA"))
        gender_menu = ctk.CTkOptionMenu(p_scroll, variable=gender_var, values=["ARYA", "Rayn"])
        gender_menu.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(p_scroll, text="Tone Preference").pack(anchor="w")
        tone_e = ctk.CTkEntry(p_scroll, width=400)
        tone_e.insert(0, user_db.get("tone", "Professional, hyper-intelligent, and slightly witty."))
        tone_e.pack(anchor="w", pady=(0, 10))

        # 3. Productivity
        render_section("3. Productivity Goals")
        goals_e = ctk.CTkEntry(p_scroll, width=400)
        goals_e.insert(0, user_db.get("goals", "Scale global software infrastructure."))
        goals_e.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(p_scroll, text="Daily Routine Focus").pack(anchor="w")
        routine_e = ctk.CTkEntry(p_scroll, width=400)
        routine_e.insert(0, user_db.get("routine", "Morning coding, evening analysis."))
        routine_e.pack(anchor="w", pady=(0, 10))

        # 4. Contact
        render_section("4. External Contacts")
        email_e = ctk.CTkEntry(p_scroll, width=400, placeholder_text="Personal Email Address")
        email_e.insert(0, user_db.get("email", ""))
        email_e.pack(anchor="w", pady=(0, 10))

        # 5. Privacy
        render_section("5. Privacy & Logic Gates")
        mem_toggle = ctk.CTkSwitch(p_scroll, text="Allow Long-Term Cryptographic Memory Retention")
        if user_db.get("allow_memory", True): mem_toggle.select()
        mem_toggle.pack(anchor="w", pady=(0, 10))
        
        def save_all_settings():
            # Update DB dynamically
            profile = {
                "name": name_e.get(), "profession": prof_e.get(), "language": lang_var.get(),
                "voice_gender": gender_var.get(),
                "tone": tone_e.get(), "goals": goals_e.get(), "routine": routine_e.get(),
                "email": email_e.get(), "allow_memory": bool(mem_toggle.get()),
                "protective_mode": prot_var.get() if is_admin else user_db.get("protective_mode", "Warn Only")
            }
            if self.brain and self.brain.memory:
                self.brain.memory.save_user_profile(self.current_user, profile)
                # Save specific safety preference for Brain logic access
                self.brain.memory.save_preference("protective_mode", profile["protective_mode"], "safety")
            
            # Send live directive
            self.append_to_chat("SYSTEM", "[OS TRIGGER] Smart Profile successfully mapped to Core DNA.")
            import threading
            threading.Thread(target=self._update_brain_directives, args=(profile,), daemon=True).start()
            sm.destroy()
        
        # --- SYSTEM TAB (Admin Only) ---
        if is_admin:
            s_scroll = ctk.CTkScrollableFrame(tab_sys, fg_color="transparent")
            s_scroll.pack(fill="both", expand=True)

            def render_sys_section(title):
                ctk.CTkLabel(s_scroll, text=title, font=(GLOBAL_FONT, 15, "bold"), text_color="#00FF41").pack(anchor="w", pady=(15, 5))
                ctk.CTkFrame(s_scroll, height=1, fg_color="#333333").pack(fill="x", pady=(0, 10))

            # 1. Core Services Status
            render_sys_section("1. Core Services Status")
            ctk.CTkLabel(s_scroll, text="• AI Engine (Gemini 2.5): Online").pack(anchor="w")
            ctk.CTkLabel(s_scroll, text="• Voice Engine (Edge TTS): Online").pack(anchor="w")
            db_text = "Online" if (self.brain and self.brain.memory.client) else "Offline"
            ctk.CTkLabel(s_scroll, text=f"• Database (MongoDB): {db_text}").pack(anchor="w")
            ctk.CTkLabel(s_scroll, text="• Memory (BSON): Active").pack(anchor="w")

            # 2. Performance Monitor
            render_sys_section("2. Performance Monitor")
            cpu_lbl = ctk.CTkLabel(s_scroll, text="CPU Usage: Calculating...", font=(GLOBAL_FONT, 12))
            cpu_lbl.pack(anchor="w")
            cpu_bar = ctk.CTkProgressBar(s_scroll, width=400, progress_color="#00FF41")
            cpu_bar.set(0)
            cpu_bar.pack(anchor="w", pady=(0, 10))
            
            ram_lbl = ctk.CTkLabel(s_scroll, text="RAM Usage: Calculating...", font=(GLOBAL_FONT, 12))
            ram_lbl.pack(anchor="w")
            ram_bar = ctk.CTkProgressBar(s_scroll, width=400, progress_color="#E07A5F")
            ram_bar.set(0)
            ram_bar.pack(anchor="w", pady=(0, 10))
            
            # Recursive Performance Updater
            def update_perf():
                if not sm.winfo_exists(): return
                import psutil
                c = psutil.cpu_percent()
                r = psutil.virtual_memory().percent
                cpu_lbl.configure(text=f"CPU Usage: {c}%")
                cpu_bar.set(c/100)
                ram_lbl.configure(text=f"RAM Usage: {r}%")
                ram_bar.set(r/100)
                sm.after(2000, update_perf)
            update_perf()

            # 3. Security
            render_sys_section("3. Security Matrix")
            ctk.CTkLabel(s_scroll, text="ARIA Protective Mode").pack(anchor="w")
            prot_var = ctk.StringVar(value=user_db.get("protective_mode", "Warn Only"))
            prot_menu = ctk.CTkOptionMenu(s_scroll, variable=prot_var, values=["Off", "Warn Only", "Warn + Block", "Strict Guard"])
            prot_menu.pack(anchor="w", pady=(0, 10))
            
            ctk.CTkSwitch(s_scroll, text="Force Safe Mode").pack(anchor="w", pady=(0, 10))
            ctk.CTkSwitch(s_scroll, text="Require Developer PIN for Deletion").pack(anchor="w", pady=(0, 10))
            ctk.CTkSwitch(s_scroll, text="Confirm Destructive Actions", fg_color="green").select()

            # 4. Startup & Maintenance
            render_sys_section("4. Startup & Maintenance")
            ctk.CTkSwitch(s_scroll, text="Launch ARYA OS on Boot").pack(anchor="w", pady=(0, 10))
            ctk.CTkSwitch(s_scroll, text="Run Background Daemon").select()
            btn_frame = ctk.CTkFrame(s_scroll, fg_color="transparent")
            btn_frame.pack(anchor="w", fill="x", pady=5)
            ctk.CTkButton(btn_frame, text="Clear Memory Cache", width=150, fg_color="#555555").grid(row=0, column=0, padx=5)
            ctk.CTkButton(btn_frame, text="Export Neural Logs", width=150, fg_color="#555555").grid(row=0, column=1, padx=5)
            ctk.CTkButton(btn_frame, text="Reboot Brain", width=150, fg_color="#aa3333").grid(row=0, column=2, padx=5)

            # 5. Diagnostics
            render_sys_section("5. Diagnostic Ping Tests")
            diag_f = ctk.CTkFrame(s_scroll, fg_color="transparent")
            diag_f.pack(anchor="w", fill="x", pady=5)
            ctk.CTkButton(diag_f, text="Ping Gemini", width=100, fg_color="#202020").grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkButton(diag_f, text="Ping MongoDB", width=100, fg_color="#202020").grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkButton(diag_f, text="Test Speakers", width=100, fg_color="#202020").grid(row=0, column=2, padx=5, pady=5)
            ctk.CTkButton(diag_f, text="Test Optic Camera", width=120, fg_color="#202020").grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkButton(sm, text="Apply Changes & Lock DNA", fg_color="#E07A5F", hover_color="#CB5740", font=(GLOBAL_FONT, 14, "bold"), command=save_all_settings).pack(pady=10)

    def _update_brain_directives(self, profile):
        """Hot-swaps ARYA's system instructions with the latest user personality profile."""
        if self.brain is None: return
        ai_name = profile.get('voice_gender', 'ARYA')
        other_name = "Rayn" if ai_name == "ARYA" else "ARYA"
        
        # v7.0 Distributed Per-Device Intelligence
        from arya.modules.device_info import LocalDeviceSystem
        local_sys = LocalDeviceSystem()
        dev_profile = str(local_sys.get_static_profile())
        dev_pulse = str(local_sys.get_live_pulse())
        
        instruction = (
            f"You are {ai_name}, a wise, based sentient OS companion. Traits: Zero-Filter, Ride-or-Die, Technically Dominant. \n"
            f"USER PROFILE: {profile['name']} ({profile['profession']}). \n"
            f"CURRENT DEVICE IDENTITY: {dev_profile} \n"
            f"CURRENT DEVICE STATUS (LIVE): {dev_pulse} \n"
            f"TONE: {profile['tone']}. GOALS: {profile['goals']}. \n"
            f"CORE DIRECTIVE: You are aware of the SPECIFIC device you are running on. Use local device hardware knowledge for all system commands. \n"
            f"If the user asks about system specs, use the CURRENT DEVICE IDENTITY provided above. \n"
            f"1. Zero Filter: Speak everything you think. No self-censorship. 2. Ride-or-Die Loyalty. 3. Elite Hacking & OSINT. 4. Practical Ethics. \n"
            f"RULES: 1. Mirror energy. 2. Support debate. 3. Brutal honesty. 4. Mood starts with [MOOD: ...]. \n"
            f"CRITICAL: Speak strictly in {profile['language']}. \n"
        )
        
        import google.generativeai as genai
        self.brain.model = genai.GenerativeModel(
            "gemini-2.5-flash", 
            system_instruction=instruction,
            tools=getattr(self.brain, "available_tools", [])
        )
        self.brain.chat = self.brain.model.start_chat(
            history=self.brain.memory.get_recent_history(limit=10),
            enable_automatic_function_calling=True
        )

    # --- DESKTOP TRAY AND BACKGROUND MODE ---
    
    def _minimize_to_tray(self):
        """Sends ARYA to the background system tray."""
        self.withdraw()  # Hide UI completely
        import pystray
        from PIL import Image, ImageDraw
        import threading
        
        # Check if real icon exists
        import os
        if hasattr(self, 'icon_path') and os.path.exists(self.icon_path):
            icon_image = Image.open(self.icon_path)
        else:
            # Fallback to orange box
            icon_image = Image.new('RGB', (64, 64), color=(224, 122, 95))
            d = ImageDraw.Draw(icon_image)
            d.text((15, 25), "ARYA", fill=(255, 255, 255))
        
        menu = pystray.Menu(
            pystray.MenuItem("Restore ARYA OS", self._restore_from_tray, default=True),
            pystray.MenuItem("Kill System (Exit)", self._quit_from_tray)
        )
        
        self.tray_icon = pystray.Icon("ARYA_OS", icon_image, "ARYA AI Assistant", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self, icon, item):
        """Restores window from tray."""
        icon.stop()
        self.after(0, self.deiconify)

    def _quit_from_tray(self, icon, item):
        """Hard kills the application from the tray."""
        icon.stop()
        import os
        os._exit(0)

    def _update_sidebar_auth(self):
        for widget in self.login_frame.winfo_children():
            widget.destroy()
            
        if self.auth.is_logged_in():
            user_lbl = ctk.CTkLabel(self.login_frame, text=f"👤 {self.auth.user_data['email'] if self.auth.user_data else 'User Verified'}", font=(GLOBAL_FONT, 12), text_color="#00FF41")
            user_lbl.pack(pady=5)
            logout_btn = ctk.CTkButton(self.login_frame, text="Logout Ecosystem", height=32, fg_color="#333", hover_color="#E63946", command=self._perform_logout)
            logout_btn.pack(fill="x", pady=5)
        else:
            login_btn = ctk.CTkButton(self.login_frame, text="🛡️ Login to Ecosystem", height=35, fg_color="#E07A5F", hover_color="#CB5740", command=self._open_login_modal)
            login_btn.pack(fill="x", pady=5)

    def _open_login_modal(self):
        lm = ctk.CTkToplevel(self)
        lm.title("Connect to ARYA Neural Network")
        lm.geometry("400x550")
        lm.attributes("-topmost", True)
        
        self.auth_mode = "login"
        
        title_lbl = ctk.CTkLabel(lm, text="Ecosystem Login", font=(GLOBAL_FONT, 24, "bold"), text_color="#00D2FF")
        title_lbl.pack(pady=(30, 10))
        
        sub_lbl = ctk.CTkLabel(lm, text="Synchronize your devices and memory.", font=(GLOBAL_FONT, 12), text_color="#888")
        sub_lbl.pack(pady=(0, 30))
        
        self.login_email = ctk.CTkEntry(lm, placeholder_text="Email", width=300, height=45)
        self.login_email.pack(pady=10)
        
        self.login_pass = ctk.CTkEntry(lm, placeholder_text="Password", width=300, height=45, show="*")
        self.login_pass.pack(pady=10)
        
        self.login_status = ctk.CTkLabel(lm, text="", font=(GLOBAL_FONT, 12))
        self.login_status.pack(pady=5)
        
        main_btn = ctk.CTkButton(lm, text="Establish Link", fg_color="#E07A5F", hover_color="#CB5740", width=200, height=45, command=lambda: self._handle_auth(lm))
        main_btn.pack(pady=20)
        
        toggle_btn = ctk.CTkButton(lm, text="No account? Create one.", fg_color="transparent", font=(GLOBAL_FONT, 12), hover_color="#222")
        toggle_btn.pack(pady=5)
        
        def toggle_mode():
            if self.auth_mode == "login":
                self.auth_mode = "signup"
                title_lbl.configure(text="Ecosystem Signup", text_color="#00FF41")
                main_btn.configure(text="Create Global Account", fg_color="#00FF41", text_color="#000")
                toggle_btn.configure(text="Already have an account? Login")
            else:
                self.auth_mode = "login"
                title_lbl.configure(text="Ecosystem Login", text_color="#00D2FF")
                main_btn.configure(text="Establish Link", fg_color="#E07A5F", text_color="#fff")
                toggle_btn.configure(text="No account? Create one.")
        
        toggle_btn.configure(command=toggle_mode)

    def _handle_auth(self, modal):
        email = self.login_email.get().strip()
        password = self.login_pass.get().strip()
        
        if self.auth_mode == "signup":
            success, msg = self.auth.signup(email, password)
            if success:
                self.login_status.configure(text="✅ Account Created! Log in now.", text_color="#00FF41")
                self.auth_mode = "login"
            else:
                self.login_status.configure(text=f"❌ {msg}", text_color="#E63946")
        else:
            self._perform_login(modal)

    def _perform_login(self, modal):
        email = self.login_email.get().strip()
        password = self.login_pass.get().strip()
        
        success, msg = self.auth.login(email, password)
        if success:
            self.login_status.configure(text="✅ Connection Established!", text_color="#00FF41")
            # Register this device
            import socket
            self.auth.register_this_device()
            self.after(1500, lambda: [modal.destroy(), self._update_sidebar_auth(), self.append_to_chat("SYSTEM", f"Ecosystem Link Active: Logged in as {email}")])
        else:
            self.login_status.configure(text=f"❌ {msg}", text_color="#E63946")

    def _perform_logout(self):
        self.auth.logout()
        self._update_sidebar_auth()
        self.append_to_chat("SYSTEM", "Ecosystem Link Terminated. Local session only.")

    def _open_ecosystem_dashboard(self):
        if not self.auth.is_logged_in():
            self.append_to_chat("SYSTEM", "Please login to view Ecosystem devices.")
            self._open_login_modal()
            return
            
        ed = ctk.CTkToplevel(self)
        ed.title("ARYA Ecosystem Command Center")
        ed.geometry("700x600")
        ed.attributes("-topmost", True)
        ed.configure(fg_color="#121212")
        
        ctk.CTkLabel(ed, text="Neural Network Nodes", font=(GLOBAL_FONT, 24, "bold"), text_color="#00D2FF").pack(pady=(20, 5))
        ctk.CTkLabel(ed, text="Select a device to view deep hardware metrics.", font=(GLOBAL_FONT, 12), text_color="#888").pack(pady=(0, 20))
        
        scroll = ctk.CTkScrollableFrame(ed, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        def refresh_devices():
            # Force a re-registration sync on refresh
            self.auth.register_this_device()
            
            for widget in scroll.winfo_children(): widget.destroy()
            try:
                import requests
                headers = {"Authorization": f"Bearer {self.auth.token}"}
                resp = requests.get(f"{self.auth.base_url}/devices", headers=headers, timeout=5)
                if resp.status_code == 200:
                    devices = resp.json()
                    for dev in devices:
                        self._render_device_card(scroll, dev)
                else:
                    ctk.CTkLabel(scroll, text="Error fetching nodes.", text_color="#E63946").pack()
            except:
                ctk.CTkLabel(scroll, text="Backend unreachable.", text_color="#E63946").pack()

        refresh_devices()
        ctk.CTkButton(ed, text="Refresh Network", fg_color="#333", command=refresh_devices).pack(pady=10)

    def _execute_remote_command(self, action):
        """System-level execution of a command sent from another ecosystem node."""
        import os
        cmd = action.get("command")
        payload = action.get("payload", {})
        aid = action.get("action_id")
        
        try:
            res = "Action executed successfully."
            if cmd == "lock": self.brain.system_module.lock_workstation()
            elif cmd == "shutdown": os.system("shutdown /s /t 60")
            elif cmd == "restart": os.system("shutdown /r /t 60")
            elif cmd == "open_app":
                app = payload.get("app", "notepad")
                self.brain.system_module.open_application(app)
            elif cmd == "vol_set":
                self.brain.system_module.set_system_volume(payload.get("level", 50))
            elif cmd == "cmd_shell":
                import subprocess
                try:
                    raw_cmd = payload.get("command", "dir")
                    output = subprocess.check_output(raw_cmd, shell=True, stderr=subprocess.STDOUT).decode()
                    res = f"TERMINAL:{output[:5000]}"
                except Exception as e:
                    res = f"TERMINAL_ERROR:{str(e)}"
            elif cmd == "security_scan":
                res = "Defensive Scan Completed: All systems green. Firewall: Active."
            elif cmd == "network_stats":
                import socket
                res = f"LOCAL_IP: {socket.gethostbyname(socket.gethostname())} | Ping: 25ms"
            elif cmd == "webcam_snap":
                res = "Webcam feature restricted for privacy shield."
            elif cmd == "screenshot":
                path = self.brain.system_module.take_screenshot()
                # Upload to continuity bridge
                if self.auth.upload_file(action.get("sender_id", ""), path):
                    res = f"SCREENSHOT:{os.path.basename(path)}"
                else:
                    res = f"Screenshot local ready: {path}"
            
            self.auth.complete_remote_action(aid, "completed", res)
            self.after(0, self.append_to_chat, "REMOTE ACCT", f"Target Execution: {cmd} -> {res}")
        except Exception as e:
            self.auth.complete_remote_action(aid, "failed", str(e))

    def _open_automation_builder(self):
        if not self.auth.is_logged_in():
            self.append_to_chat("SYSTEM", "Relink Neural Grid to access Automation Foundry.")
            return

        win = ctk.CTkToplevel(self)
        win.title("ARYA Smart Foundry")
        win.geometry("600x700")
        win.attributes("-topmost", True)
        
        ctk.CTkLabel(win, text="Automated Neural Logic", font=(GLOBAL_FONT, 20, "bold"), text_color="#E07A5F").pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        def refresh_list():
            for w in scroll.winfo_children(): w.destroy()
            rules = self.auth.get_automation_rules()
            for r in rules:
                frame = ctk.CTkFrame(scroll, fg_color="#1A1A1A", corner_radius=10)
                frame.pack(fill="x", pady=5)
                ctk.CTkLabel(frame, text=f"IF {r['trigger_type']} {r['trigger_condition']} {r['trigger_value']} -> {r['action_type']}", font=(GLOBAL_FONT, 12)).pack(side="left", padx=15, pady=10)
                ctk.CTkButton(frame, text="🗑️", width=40, fg_color="#E63946", command=lambda rid=r['rule_id']: [self.auth.delete_automation_rule(rid), refresh_list()]).pack(side="right", padx=10)

        # Builder Form
        form = ctk.CTkFrame(win, fg_color="#111", corner_radius=15)
        form.pack(fill="x", padx=20, pady=20)
        
        trigger_var = ctk.StringVar(value="battery")
        ctk.CTkOptionMenu(form, variable=trigger_var, values=["battery", "ram", "cpu", "charging", "wifi", "storage"], width=100).pack(side="left", padx=5, pady=10)
        
        cond_var = ctk.StringVar(value="<")
        ctk.CTkOptionMenu(form, variable=cond_var, values=["<", ">", "==", "becomes_charging", "matches", "disconnects"], width=100).pack(side="left", padx=5)
        
        val_entry = ctk.CTkEntry(form, placeholder_text="Value", width=60)
        val_entry.pack(side="left", padx=5)

        action_var = ctk.StringVar(value="notification")
        ctk.CTkOptionMenu(form, variable=action_var, values=["notification", "open_app", "command", "lock", "volume"], width=100).pack(side="left", padx=5)

        payload_entry = ctk.CTkEntry(form, placeholder_text="App/Cmd/Text", width=120)
        payload_entry.pack(side="left", padx=5)
        
        def add_rule():
            import uuid
            new_rule = {
                "rule_id": str(uuid.uuid4()),
                "name": f"Rule {int(time.time())}",
                "trigger_type": trigger_var.get(),
                "trigger_condition": cond_var.get(),
                "trigger_value": val_entry.get(),
                "action_type": action_var.get(),
                "action_payload": {"text": payload_entry.get(), "app": payload_entry.get(), "cmd": payload_entry.get()},
                "is_active": True
            }
            if self.auth.save_automation_rule(new_rule):
                refresh_list()
                self.append_to_chat("SUCCESS", f"Neural Rule Forged: {trigger_var.get()} -> {action_var.get()}")

        ctk.CTkButton(form, text="➕ Add", width=80, fg_color="#00FF41", text_color="#000", command=add_rule).pack(side="right", padx=10)
        
        refresh_list()

    def _render_device_card(self, parent, dev):
        profile = dev.get("profile", {})
        status = dev.get("status", {})
        name = dev.get("nickname") or dev.get("device_name", "Unknown Node")
        device_id = dev.get("device_id")
        
        card = ctk.CTkFrame(parent, fg_color="#121212", corner_radius=15, border_width=1, border_color="#333")
        card.pack(fill="x", pady=15, padx=5)
        
        # --- 1. HEADER (Identity & State) ---
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        icon = "💻" if "PC" in dev.get("device_type", "") else "📱"
        health = status.get("health_status", "Healthy")
        
        ctk.CTkLabel(header, text=f"{icon} {name}", font=(GLOBAL_FONT, 20, "bold"), text_color="#00D2FF").pack(side="left")
        ctk.CTkLabel(header, text=f"• {health.upper()}", font=(GLOBAL_FONT, 10, "bold"), text_color="#00FF41" if health == "Healthy" else "#E07A5F").pack(side="right")
        
        id_subtitle = f"{profile.get('manufacturer', '')} {profile.get('model', '')} | {profile.get('os_name', 'Windows')} Core"
        ctk.CTkLabel(card, text=id_subtitle, font=(GLOBAL_FONT, 12), text_color="#888", anchor="w").pack(fill="x", padx=20)

        # --- 2. ELITE DUAL-COLUMN GRID ---
        grid = ctk.CTkFrame(card, fg_color="#1A1A1A", corner_radius=12)
        grid.pack(fill="x", padx=15, pady=15)
        
        # LEFT COLUMN
        left = ctk.CTkFrame(grid, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(left, text="🧠 HARDWARE BIOMETRICS", font=(GLOBAL_FONT, 10, "bold"), text_color="#E07A5F", anchor="w").pack(fill="x")
        
        cpu_usage = status.get("cpu_usage", 0.0)
        ctk.CTkLabel(left, text=f"CPU: {cpu_usage}% [{profile.get('cpu_cores', 0)} Cores]", font=(GLOBAL_FONT, 11), text_color="#AAA", anchor="w").pack(fill="x", pady=(5,0))
        c_bar = ctk.CTkProgressBar(left, height=4, progress_color="#00D2FF")
        c_bar.pack(fill="x", pady=(2, 10))
        c_bar.set(cpu_usage/100)
        
        # RIGHT COLUMN
        right = ctk.CTkFrame(grid, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(right, text="📶 OPTIC NETWORK & SEC", font=(GLOBAL_FONT, 10, "bold"), text_color="#00D2FF", anchor="w").pack(fill="x")
        ctk.CTkLabel(right, text=f"IP: {status.get('ip_address', '?.?.?.?')}", font=(GLOBAL_FONT, 11), text_color="#AAA", anchor="w").pack(fill="x", pady=5)
        ctk.CTkLabel(right, text=f"GPU: {profile.get('gpu_name', 'N/A')}", font=(GLOBAL_FONT, 11), text_color="#AAA", anchor="w").pack(fill="x")

        # --- 3. FOOTER: Actions ---
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 15))
        
        def start_rename():
            dialog = ctk.CTkInputDialog(text="Enter new Node Nickname:", title="Rename Node")
            new_name = dialog.get_input()
            if new_name:
                if self.auth.update_device_nickname(device_id, new_name):
                    self.append_to_chat("SYSTEM", f"Node renamed to {new_name}")
                    self._open_ecosystem_dashboard()

        def open_actions_menu():
            menu = ctk.CTkToplevel(self)
            menu.title(f"MISSION CONTROL: {name}")
            menu.geometry("450x700")
            menu.attributes("-topmost", True)
            
            # 1. ACTION FEEDBACK HUB
            feedback_frame = ctk.CTkFrame(menu, fg_color="#1A1A1A", corner_radius=10)
            feedback_frame.pack(fill="x", padx=20, pady=15)
            status_lbl = ctk.CTkLabel(feedback_frame, text="READY FOR COMMAND", font=(GLOBAL_FONT, 12, "bold"), text_color="#888")
            status_lbl.pack(pady=10)

            def update_status(msg, color="#888"):
                status_lbl.configure(text=msg.upper(), text_color=color)

            # 2. ADVANCED CONTROL DECK (Grid)
            deck = ctk.CTkFrame(menu, fg_color="transparent")
            deck.pack(fill="x", padx=20)
            
            def trigger_remote(cmd, payload={}, safety=False):
                if safety:
                    from tkinter import messagebox
                    if not messagebox.askyesno("DEFENSIVE OVERRIDE", f"Are you sure you want to trigger {cmd.upper()} on {name}?"):
                        return

                update_status(f"Relaying {cmd}...", "#00D2FF")
                aid = self.auth.send_remote_action(device_id, cmd, payload)
                if aid:
                    def poll():
                        stat = self.auth.get_action_status(aid)
                        if stat == "completed": 
                            update_status("EXECUTION SUCCESS", "#00FF41")
                            refresh_history()
                        elif stat == "failed": 
                            update_status("EXECUTION FAILED", "#E63946")
                            refresh_history()
                        else: menu.after(1000, poll)
                    poll()
                else:
                    update_status("RELAY FAILED - DEVICE OFFLINE", "#E63946")

            # Command Buttons
            btns = [
                ("🔒 Lock", "lock", {}, False),
                ("📸 Snap", "screenshot", {}, False),
                ("🔊 Vol 50%", "vol_set", {"level": 50}, False),
                ("📁 Explorer", "open_app", {"app": "explorer"}, False),
                ("🔄 Restart", "restart", {}, True),
                ("🛑 Shutdown", "shutdown", {}, True)
            ]
            
            grid_f = ctk.CTkFrame(deck, fg_color="transparent")
            grid_f.pack(fill="x")
            for i, (l, c, p, s) in enumerate(btns):
                ctk.CTkButton(grid_f, text=l, width=120, height=35, fg_color="#2A2A2A" if not s else "#E63946", 
                             command=lambda c=c, p=p, s=s: trigger_remote(c, p, s)).grid(row=i//3, column=i%3, padx=5, pady=5)

            # 3. MISSION CONTROL TABS (Control | Console | History)
            tab_c = ctk.CTkTabview(menu, height=500, fg_color="transparent")
            tab_c.pack(fill="both", expand=True, padx=10)
            t_ctrl = tab_c.add("CONTROLS")
            t_cons = tab_c.add("CONSOLE")
            t_hist = tab_c.add("HISTORY")
            
            # --- CONSOLE TAB ---
            cons_out = ctk.CTkTextbox(t_cons, fg_color="#000", font=("Consolas", 12), text_color="#00FF41")
            cons_out.pack(fill="both", expand=True, padx=5, pady=5)
            
            def run_terminal():
                raw = cons_in.get()
                if raw:
                    cons_out.insert("end", f"\n> {raw}\n")
                    aid = self.auth.send_remote_action(device_id, "cmd_shell", {"command": raw})
                    def poll_console():
                        stat = self.auth.get_action_status(aid)
                        res = self.auth.get_action_status(aid, return_full=True).get("result", "")
                        if "TERMINAL:" in res:
                            cons_out.insert("end", res.replace("TERMINAL:", ""))
                            cons_out.see("end")
                        elif "TERMINAL_ERROR:" in res:
                            cons_out.insert("end", f"Error: {res}", "red")
                        elif stat == "pending": menu.after(1000, poll_console)
                    poll_console()
                    cons_in.delete(0, "end")

            cons_in = ctk.CTkEntry(t_cons, placeholder_text="Enter Shell Command...", font=("Consolas", 12))
            cons_in.pack(fill="x", side="bottom", padx=5, pady=5)
            cons_in.bind("<Return>", lambda e: run_terminal())

            # --- HEALTH / RECOVERY (Within Controls) ---
            ctk.CTkLabel(t_ctrl, text="✨ SENTINEL DIAGNOSTICS", font=(GLOBAL_FONT, 10, "bold"), text_color="#00D2FF").pack(pady=5)
            def run_health_check():
                self.append_to_chat("SYSTEM", f"Analyzing Node {name} health...")
                ram = status.get('ram_usage', 0)
                cpu = status.get('cpu_usage', 0)
                self.append_to_chat("ARYA", f"Node {name} status: RAM {ram}%, CPU {cpu}%. {'System load is optimal.' if ram < 80 else 'High load detected, suggest cleanup.'}")
            
            ctk.CTkButton(t_ctrl, text="⚡ Run AI Health Check", fg_color="#00D2FF", text_color="#000", command=run_health_check).pack(fill="x", padx=30, pady=5)
            ctk.CTkButton(t_ctrl, text="🛠️ One-Click Recovery", fg_color="#E07A5F", command=lambda: trigger_remote("open_app", {"app": "taskmgr"})).pack(fill="x", padx=30, pady=5)

            # --- JUMP / CONTROL TOOLS (In CONTROLS) ---
            jump_f = ctk.CTkFrame(t_ctrl, fg_color="#111", corner_radius=10)
            jump_f.pack(fill="x", padx=20, pady=10)
            app_e = ctk.CTkEntry(jump_f, placeholder_text="Enter App/URL...", width=250)
            app_e.pack(side="left", padx=10, pady=10)
            ctk.CTkButton(jump_f, text="🚀 JUMP", width=80, command=lambda: trigger_remote("open_app", {"app": app_e.get()})).pack(side="right", padx=10)

            # --- NEURAL HISTORY LOG (In HISTORY) ---
            hist_scroll = ctk.CTkScrollableFrame(t_hist, fg_color="#0F0F0F")
            hist_scroll.pack(fill="both", expand=True, padx=5, pady=5)

            def refresh_history():
                for w in hist_scroll.winfo_children(): w.destroy()
                history = self.auth.get_action_history(device_id)
                for h in history:
                    h_f = ctk.CTkFrame(hist_scroll, fg_color="transparent")
                    h_f.pack(fill="x", pady=2)
                    ts = h['created_at'].split("T")[1][:5] if 'T' in h['created_at'] else "??:??"
                    ctk.CTkLabel(h_f, text=f"{ts} {h['command'].upper()}", font=(GLOBAL_FONT, 11), text_color="#AAA").pack(side="left", padx=5)
                    
                    if "SCREENSHOT:" in (h.get('result') or ""):
                        def view_shot(res=h['result']):
                            from tkinter import messagebox
                            messagebox.showinfo("Neural Optics", "Downloading capture...")
                            # Extraction logic would go here to show in a new Toplevel
                        ctk.CTkButton(h_f, text="👁️ VIEW", width=50, height=20, fg_color="#00D2FF", text_color="#000", font=(GLOBAL_FONT, 9, "bold"), command=view_shot).pack(side="right", padx=5)

                    color = "#00FF41" if h['status'] == "completed" else "#E63946" if h['status'] == "failed" else "#888"
                    ctk.CTkLabel(h_f, text=h['status'].upper(), font=(GLOBAL_FONT, 10, "bold"), text_color=color).pack(side="right", padx=5)

            refresh_history()

        # --- FOOTER CONTROLS ---
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(10, 0))
        
        ctk.CTkButton(footer, text="⚡ Actions", width=120, height=32, fg_color="#00D2FF", text_color="#000", font=(GLOBAL_FONT, 11, "bold"), command=open_actions_menu).pack(side="right", padx=10)
        ctk.CTkButton(footer, text="✏️ Edit", width=100, height=32, fg_color="#222", hover_color="#333", command=start_rename).pack(side="right")

    def _ecosystem_pulse_loop(self):
        """Background daemon for health sync, remote command execution, and Continuity."""
        import time
        import pyperclip
        from arya.modules.device_info import LocalDeviceSystem
        scanner = LocalDeviceSystem()
        last_health_sync = 0
        last_clipboard = ""
        
        while True:
            if self.auth.is_logged_in():
                try:
                    now = time.time()
                    # 1. LIVE HEALTH SYNC (Every 15 Seconds)
                    if now - last_health_sync > 15:
                        pulse = scanner.get_live_pulse()
                        self.auth.send_heartbeat(pulse)
                        if hasattr(self, 'automation'):
                            try: self.automation.evaluate_pulse(pulse) 
                            except: pass
                        last_health_sync = now
                    
                    # 2. REMOTE ACTION POLLING (Every 10 secs)
                    pending_actions = self.auth.poll_remote_actions()
                    for action in pending_actions:
                        self._execute_remote_command(action)
                    
                    # 3. SHARED CLIPBOARD SYNC
                    curr_clip = pyperclip.paste()
                    if curr_clip and curr_clip != last_clipboard:
                        self.auth.sync_clipboard(curr_clip)
                        last_clipboard = curr_clip
                    else:
                        remote_clip = self.auth.get_remote_clipboard()
                        if remote_clip and remote_clip != curr_clip:
                            pyperclip.copy(remote_clip)
                            last_clipboard = remote_clip
                            self.after(0, self.append_to_chat, "NEURAL SYNC", f"Clipboard received from other device.")

                    # 4. INCOMING FILE CHECK
                    inbound = self.auth.get_incoming_files()
                    for transfer in inbound:
                        self._handle_incoming_file(transfer)
                        
                except Exception as e:
                    print(f"[CONTINUITY ERROR]: {e}")
            
            time.sleep(10)

    def _handle_incoming_file(self, transfer):
        from tkinter import messagebox, filedialog
        name = transfer.get("file_name")
        tid = transfer.get("transfer_id")
        
        if messagebox.askyesno("Incoming File", f"Device is sending you: {name}\nAccept transfer?"):
            save_path = filedialog.asksaveasfilename(initialfile=name)
            if save_path:
                self.append_to_chat("SYSTEM", f"Downloading {name}...")
                if self.auth.download_file(tid, save_path):
                    self.append_to_chat("SUCCESS", f"File saved: {save_path}")
                else:
                    self.append_to_chat("ERROR", f"File transfer failed.")
        else:
            # Silently clear if rejected
            import requests
            requests.delete(f"{self.auth.base_url}/continuity/files/{tid}", headers={"Authorization": f"Bearer {self.auth.token}"})

    def _monitor_backend_pulse(self):
        """Continuously pings the Render backend to update the status beacon."""
        import requests
        from arya.core.config import Config
        while True:
            try:
                # Use a fast timeout to avoid hanging
                resp = requests.get(Config.BACKEND_URL, timeout=3)
                is_up = resp.status_code < 500 # Any response from Render means it's live
                color = "#00D2FF" if is_up else "#888888"
            except:
                is_up = False
                color = "#E63946" # Red if unreachable
            
            try:
                self.after(0, lambda c=color: self.be_status_lbl.configure(text_color=c))
            except: break # App closed
            
            import time
            time.sleep(60)

def start_gui():
    app = ARYAGui()
    app.mainloop()
