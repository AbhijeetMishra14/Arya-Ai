import cv2
import os
import threading
import time
import numpy as np
from PIL import Image

# SILENCE TENSORFLOW/ABSL LOG SPAM
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class VisionModule:
    """ARYA Optical Sentinel: Handles high-speed face detection and local recognition (JARVIS Style)."""
    
    def __init__(self, master_gui=None):
        self.master_gui = master_gui
        self.profiles_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profiles")
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        self.face_detector = None
        self._models_loaded = False
        self.cap = None
        self.latest_frame = None
        self.camera_lock = threading.Lock()
        
        # Start background calibration to prevent splash screen freeze
        threading.Thread(target=self._initialize_sensors, daemon=True).start()
        
        self.active_tracks = {}
        self.greet_cooldown = 1800 
        self.last_greeted_times = {}
        
        self._is_monitoring = True
        self._camera_busy = False
        
        # Start persistent camera stream
        threading.Thread(target=self._camera_service_loop, daemon=True).start()

    def _initialize_sensors(self):
        """Background calibration of neural vision models."""
        try:
            # Attempt standard MediaPipe import
            import mediapipe as mp
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detector = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
            self._models_loaded = True
            print("[SYSTEM]: Optical sentinel calibrated and online.")
        except Exception as e:
            # Fallback for specific installation layouts
            try:
                import mediapipe.python.solutions.face_detection as mp_face_detection
                self.mp_face_detection = mp_face_detection
                self.face_detector = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
                self._models_loaded = True
                print("[SYSTEM]: Optical sentinel calibrated via fallback.")
            except Exception as e2:
                print(f"[SYSTEM WARNING]: MediaPipe initialization failed. Falling back to OpenCV Haar Cascades. {e2}")
                try:
                    self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    self._models_loaded = True
                    self.face_detector = "CV2"
                    print("[SYSTEM]: Optical sentinel calibrated via OpenCV fallback.")
                except Exception as e3:
                    print(f"[SYSTEM ERROR]: Vision sensor calibration failed: All fallbacks exhausted. {e3}")

    def _camera_service_loop(self):
        """Persistent background camera stream: Opens once, stays alive."""
        while True:
            try:
                if self._is_monitoring:
                    with self.camera_lock:
                        if self.cap is None or not self.cap.isOpened():
                            # Fast DSHOW initialization
                            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        
                        ret, frame = self.cap.read()
                        if ret:
                            self.latest_frame = frame
                else:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                
                time.sleep(0.01) # High frequency capture
            except Exception as e:
                print(f"[CAMERA SERVICE ERROR]: {e}")
                time.sleep(2)

    def set_monitoring(self, state: bool):
        self._is_monitoring = state

    def get_latest_frame(self):
        """Safe access to the current frame buffer."""
        with self.camera_lock:
            return self.latest_frame if self.latest_frame is not None else None

    def analyze_scene(self, frame):
        """High-speed frame analysis using local models."""
        if not self._is_monitoring or frame is None or not self._models_loaded:
            return []

        # 1. MediaPipe Detection (Ultra fast)
        if self.face_detector != "CV2":
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detector.process(rgb_frame)
            
            detections = []
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, c = frame.shape
                    x, y, bw, bh = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
                    detections.append((x, y, bw, bh))
            return detections
        else:
            # 2. OpenCV Haar Cascade Fallback
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            return [(x, y, w, h) for (x, y, w, h) in faces]

    def recognize_face(self, frame, x, y, w, h):
        """Identifies a face using the local DeepFace database."""
        if not self._models_loaded: return "Unknown"
        
        # --- STABILITY CHECK: Avoid scanning if the profile DB is empty ---
        try:
            # Look for subdirectories or jpg files in profiles_dir
            has_profiles = any(os.path.isdir(os.path.join(self.profiles_dir, d)) for d in os.listdir(self.profiles_dir))
            if not has_profiles:
                return "Unknown" # Stay silent if nothing to compare against
        except:
            return "Unknown"

        try:
            from deepface import DeepFace
            # Crop precisely to the face
            face_crop = frame[max(0, y-20):min(frame.shape[0], y+h+20), max(0, x-20):min(frame.shape[1], x+w+20)]
            if face_crop.size == 0: return "Unknown"
            
            # Simple local search
            res = DeepFace.find(face_crop, db_path=self.profiles_dir, enforce_detection=False, silent=True, model_name="VGG-Face")
            if res and len(res) > 0 and not res[0].empty:
                identity = res[0].iloc[0]['identity']
                distance = res[0].iloc[0]['distance']
                
                # VGG-Face threshold is usually ~0.4 for distance
                if distance < 0.4:
                    name = os.path.basename(os.path.dirname(identity)).replace("_", " ").title()
                    return name
        except Exception as e:
            # Only print critical errors, ignore "no item found" library noise
            if "item found" not in str(e).lower():
                print(f"[VISION ERROR]: {e}")
        return "Unknown"

    def enroll_new_profile(self, name, frames):
        """Physically saves face images for a new user Profile."""
        folder = os.path.join(self.profiles_dir, name.replace(" ", "_").lower())
        os.makedirs(folder, exist_ok=True)
        
        for i, f in enumerate(frames):
            path = os.path.join(folder, f"sample_{i}.jpg")
            cv2.imwrite(path, f)
        
        # Clear DeepFace cache to recognize new profile immediately
        cache_path = os.path.join(self.profiles_dir, "representations_vgg_face.pkl")
        if os.path.exists(cache_path):
            os.remove(cache_path)
            
        return True
