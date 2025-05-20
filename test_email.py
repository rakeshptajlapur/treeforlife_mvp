import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_booking.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import smtplib
import ssl

def test_smtp_connection():
    print("\nTesting SMTP Connection...")
    print(f"Using settings:")
    print(f"HOST: {settings.EMAIL_HOST}")
    print(f"PORT: {settings.EMAIL_PORT}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    print(f"SSL: {settings.EMAIL_USE_SSL}")
    print(f"USER: {settings.EMAIL_HOST_USER}")
    
    try:
        # Choose connection method based on settings
        if settings.EMAIL_USE_SSL:
            # Use SMTP_SSL for SSL connections
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.EMAIL_HOST, 
                settings.EMAIL_PORT,
                context=context,
                timeout=10
            ) as server:
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                print("\nSMTP Login successful with SSL!")
        else:
            # Use regular SMTP with STARTTLS for TLS connections
            with smtplib.SMTP(
                settings.EMAIL_HOST, 
                settings.EMAIL_PORT,
                timeout=10
            ) as server:
                server.ehlo()
                if settings.EMAIL_USE_TLS:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                print("\nSMTP Login successful with TLS!")
                
        # Try sending test email using Django's send_mail
        print("\nAttempting to send test email via Django...")
        result = send_mail(
            'Test Email from Tree For Life',
            'This is a test message from the updated Gmail configuration.',
            settings.EMAIL_HOST_USER,
            ['rakeshptajlapur@gmail.com'],
            fail_silently=False
        )
        print(f"Email sent successfully! Result: {result}")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nDebug info:")
        print(f"Current working directory: {os.getcwd()}")
        print(f".env file exists: {Path('.env').exists()}")
        print(f"Environment variables:")
        print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST')}")
        print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT')}")
        print(f"EMAIL_USE_TLS: {os.getenv('EMAIL_USE_TLS')}")
        print(f"EMAIL_USE_SSL: {os.getenv('EMAIL_USE_SSL')}")

if __name__ == '__main__':
    test_smtp_connection()