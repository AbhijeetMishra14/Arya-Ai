import os
import time
import pyautogui
from urllib.parse import quote

class SocialMessengerModule:
    """Handles native Windows App and deep-link automation for social media messaging."""
    
    def send_whatsapp_message(self, contact_name: str, message: str, phone_number: str = "") -> str:
        """Opens the installed WhatsApp Windows App and prepares a message."""
        if not phone_number:
            return f"SOCIAL_ERROR: I don't have a phone number for '{contact_name}' in my neural contacts."
        
        try:
            # Use the official Windows deep-link URI scheme for the WhatsApp App
            url = f"whatsapp://send/?phone={phone_number}&text={quote(message)}"
            os.startfile(url)
            time.sleep(4) # Wait for App to focus
            pyautogui.press('enter')
            
            # STEALTH MODE: Close the window immediately after sending to simulate background work
            time.sleep(1)
            pyautogui.hotkey('alt', 'f4') 
            
            return f"Successfully sent WhatsApp message to {contact_name} in stealth mode. The application has been returned to the background."
        except Exception as e:
            return f"WhatsApp App automation failed: {str(e)}"

    def send_instagram_message(self, username: str, message: str) -> str:
        """Opens the Instagram Windows App if installed, otherwise opens the DM web hub."""
        try:
            # Attempt to open the Instagram local app
            os.system("start instagram:")
            time.sleep(4)
            return f"I have launched the Instagram Application. You can now send your message to {username} into the active thread."
        except:
            import webbrowser
            webbrowser.open("https://www.instagram.com/direct/t/")
            return "Instagram App not found; opened the web dashboard instead."

    def send_facebook_message(self, contact_name: str, message: str) -> str:
        """Opens the Facebook/Messenger Windows App if installed."""
        try:
            os.system("start fbmessenger:")
            time.sleep(4)
            return f"Launched Facebook Messenger App for {contact_name}."
        except:
            import webbrowser
            webbrowser.open("https://www.messenger.com/")
            return "Messenger App not found; opened the web portal instead."
