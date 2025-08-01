import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_booking_confirmation(full_name: str, email: str, date: str, time: str):
    """Sends a confirmation email for the booked interview."""
    recipient_email = settings.SMTP_SENDER_EMAIL

    # Create the email message
    body = (
        f"Dear {full_name},\n\n"
        f"This is a confirmation that your interview with Palm Mind Technology has been successfully booked.\n\n"
        f"Details:\n"
        f"Date: {date}\n"
        f"Time: {time}\n\n"
        f"We look forward to speaking with you.\n\n"
        f"Best regards,\n"
        f"PalmBot"
    )
    msg = MIMEText(body)
    msg['Subject'] = 'Interview Confirmation - Palm Mind Technology'
    msg['From'] = settings.SMTP_SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        print(f"Attempting to send booking confirmation email to {recipient_email}...")
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls() # Secure the connection
            server.login(settings.SMTP_SENDER_EMAIL, settings.SMTP_SENDER_PASSWORD)
            server.send_message(msg)
        print("Confirmation email sent successfully.")
    except Exception as e:
        print(f"CRITICAL: Failed to send email. Error: {e}")
