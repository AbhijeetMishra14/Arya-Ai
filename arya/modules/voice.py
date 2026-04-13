import speech_recognition as sr
import os
import io

class VoiceModule:
    """Handles Text-To-Speech (TTS) and Speech-To-Text (STT) globally."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300 # Make highly sensitive by default
        self.recognizer.pause_threshold = 0.8  # Ultra-snappy cutoff for instant response
        self.recognizer.dynamic_energy_threshold = True
        self._stop_flag = False
        
    def stop(self):
        self._stop_flag = True
        try:
            import pygame
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except:
            pass
        
    def speak(self, text: str, lang_code: str = 'English', gender: str = 'ARYA'):
        """Converts the given text to speech securely using global linguistic patterns and Azure Neural mapping."""
        self._is_speaking = True
        self._stop_flag = False
        try:
            import re
            clean_text = re.sub(r'\[MOOD:\s*[^\]]+\]', '', text, flags=re.IGNORECASE)
            clean_text = clean_text.replace('*', '').replace('#', '').strip()
            # Escape double quotes natively for the CLI
            clean_text = clean_text.replace('"', '')
            
            if not clean_text:
                return
                
            import os
            import subprocess
            import pygame
            import tempfile
            import time
            
            # Map Azure Neural Voices Dynamically via Full String Matching
            voice_code = "en-US-AriaNeural"
            if gender == "ARYA":
                if lang_code == "Spanish": voice_code = "es-ES-ElviraNeural"
                elif lang_code == "French": voice_code = "fr-FR-DeniseNeural"
                elif lang_code == "Hindi": voice_code = "hi-IN-SwaraNeural"
                elif lang_code == "Nepali": voice_code = "ne-NP-HemkalaNeural"
                elif lang_code == "Japanese": voice_code = "ja-JP-NanamiNeural"
                elif lang_code == "German": voice_code = "de-DE-KatjaNeural"
                elif lang_code == "Chinese": voice_code = "zh-CN-XiaoxiaoNeural"
                elif lang_code == "Italian": voice_code = "it-IT-ElsaNeural"
                elif lang_code == "Russian": voice_code = "ru-RU-SvetlanaNeural"
                elif lang_code == "Korean": voice_code = "ko-KR-SunHiNeural"
                else: voice_code = "en-US-AriaNeural"
            else:
                if lang_code == "Spanish": voice_code = "es-ES-AlvaroNeural"
                elif lang_code == "French": voice_code = "fr-FR-HenriNeural"
                elif lang_code == "Hindi": voice_code = "hi-IN-MadhurNeural"
                elif lang_code == "Nepali": voice_code = "ne-NP-SagarNeural"
                elif lang_code == "Japanese": voice_code = "ja-JP-KeitaNeural"
                elif lang_code == "German": voice_code = "de-DE-ConradNeural"
                elif lang_code == "Chinese": voice_code = "zh-CN-YunxiNeural"
                elif lang_code == "Italian": voice_code = "it-IT-DiegoNeural"
                elif lang_code == "Russian": voice_code = "ru-RU-DmitryNeural"
                elif lang_code == "Korean": voice_code = "ko-KR-InJoonNeural"
                else: voice_code = "en-US-GuyNeural"
            
            # Extract Mood for Dynamic Prosody (Emotional Synthesis)
            rate = "+0%"
            pitch = "+0Hz"
            mood_match = re.search(r'\[MOOD:\s*([^\]]+)\]', text, re.IGNORECASE)
            if mood_match:
                mood = mood_match.group(1).upper()
                if "SWEET" in mood:
                    rate = "-10%"
                    pitch = "+2Hz"
                elif "EXCITED" in mood:
                    rate = "+15%"
                    pitch = "+5Hz"
                elif "SAD" in mood:
                    rate = "-20%"
                    pitch = "-3Hz"
                elif "ANNOYED" in mood:
                    rate = "-5%"
                    pitch = "-5Hz"
                elif "PROFESSIONAL" in mood:
                    rate = "+5%"
                    pitch = "+0Hz"

            audio_path = os.path.join(tempfile.gettempdir(), f"arya_vocal_{int(time.time())}.mp3")
            
            # Execute Azure Edge TTS purely in native Python cleanly
            import asyncio
            import edge_tts
            
            async def generate_audio():
                communicate = edge_tts.Communicate(clean_text, voice_code, rate=rate, pitch=pitch)
                await communicate.save(audio_path)
            
            asyncio.run(generate_audio())
            
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            self._speak_session = time.time()
            session_id = self._speak_session
            
            import speech_recognition as sr
            rec = sr.Recognizer()
            source = sr.Microphone()
            
            def interrupt_callback(recognizer, audio):
                if getattr(self, '_stop_flag', False) or getattr(self, '_speak_session', 0) != session_id:
                    return
                try:
                    txt = recognizer.recognize_google(audio).lower()
                    if any(w in txt for w in ["arya", "rayn", "stop", "listen", "suno", "sunnus", "सुन", "सुनुहोस्"]):
                        self.stop()
                        if hasattr(self, 'master_gui'):
                            self.master_gui.after(0, self.master_gui.listen_voice)
                except:
                    pass
            
            try:
                with source:
                    rec.adjust_for_ambient_noise(source, duration=0.2)
                stop_bg_listen = rec.listen_in_background(source, interrupt_callback, phrase_time_limit=2.0)
            except Exception:
                stop_bg_listen = lambda wait_for_stop=False: None
            
            while pygame.mixer.music.get_busy() and not self._stop_flag:
                time.sleep(0.1)
                
            try:
                stop_bg_listen(wait_for_stop=False)
            except: pass
                
            pygame.mixer.music.unload()
            pygame.mixer.quit()
            
            if os.path.exists(audio_path):
                try: os.remove(audio_path)
                except: pass
                
        except Exception as e:
            print(f"[TTS Global Error]: {e}")
            try:
                import win32com.client
                import time
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                
                voices = speaker.GetVoices()
                if gender == "ARYA":
                    for i in range(voices.Count):
                        desc = voices.Item(i).GetDescription().lower()
                        if "zira" in desc or "hazel" in desc or "female" in desc:
                            speaker.Voice = voices.Item(i)
                            break
                else:
                    for i in range(voices.Count):
                        desc = voices.Item(i).GetDescription().lower()
                        if "david" in desc or "mark" in desc or "male" in desc:
                            speaker.Voice = voices.Item(i)
                            break
                            
                self._speak_session = time.time()
                session_id = self._speak_session
                
                import speech_recognition as sr
                rec = sr.Recognizer()
                source = sr.Microphone()
                
                def interrupt_callback(recognizer, audio):
                    if getattr(self, '_stop_flag', False) or getattr(self, '_speak_session', 0) != session_id:
                        return
                    try:
                        txt = recognizer.recognize_google(audio).lower()
                        if "arya" in txt or "rayn" in txt or "stop" in txt:
                            self.stop()
                            if hasattr(self, 'master_gui'):
                                self.master_gui.after(0, self.master_gui.listen_voice)
                    except: pass

                try:
                    with source:
                        rec.adjust_for_ambient_noise(source, duration=0.2)
                    stop_bg_listen = rec.listen_in_background(source, interrupt_callback, phrase_time_limit=2.0)
                except:
                    stop_bg_listen = lambda wait_for_stop=False: None
                
                # Speak asynchronously (Flag 1 = SVSFlagsAsync)
                speaker.Speak(text, 1)
                time.sleep(0.1) # Brief buffer 
                
                while speaker.Status.RunningState == 2 and not getattr(self, '_stop_flag', False):
                    time.sleep(0.1)
                    
                if getattr(self, '_stop_flag', False):
                    try:
                        # Purge queue (Flag 2 = SVSFPurgeBeforeSpeak)
                        speaker.Speak("", 2) 
                    except: pass
                    
                try: stop_bg_listen(wait_for_stop=False)
                except: pass
                
            except Exception as ex:
                print(f"[Offline Microsoft SAPI Error]: {ex}")
                
        import time
        self._is_speaking = False
        self._last_speak_time = time.time()

    def listen(self) -> str:
        """Listens to the microphone and returns recognized text."""
        with sr.Microphone() as source:
            print("\n[ARYA is listening... Speak now]")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                print(f"[Heard]: {text}")
                return text
            except sr.WaitTimeoutError:
                return ""
            except Exception as e:
                print(f"[Speech recognition error]: {e}")
                return ""
