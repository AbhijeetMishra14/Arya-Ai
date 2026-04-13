import smtplib
from email.message import EmailMessage
from arya.core.config import Config

class MailModule:
    """Handles sending emails via SMTP using Gmail App Passwords."""
    
    def send_email(self, to_email: str, subject: str, body: str) -> str:
        """Sends an email to the specified address. Ensure you get the recipient, subject, and body from the user before executing."""
        user = Config.GMAIL_USER
        password = Config.GMAIL_APP_PASSWORD
        
        if not user or not password:
            return "Email credentials are not configured securely. I cannot send the email."
            
        # Clean up any potential spaces from the App Password provided
        password = password.replace(" ", "")
            
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = f"ARYA Assistant <{user}>"
            msg['To'] = to_email
            
            # Connect to Gmail SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
                
            return f"Successfully sent email to {to_email} with subject '{subject}'."
        except Exception as e:
            return f"Failed to send email. Ensure the App Password is correct. Error: {str(e)}"
