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
    print(f"SSL: {settings.EMAIL_USE_SSL}")
    print(f"USER: {settings.EMAIL_HOST_USER}")
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            settings.EMAIL_HOST, 
            settings.EMAIL_PORT,
            context=context,
            timeout=10
        ) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            print("\nSMTP Login successful!")
            
            # Try sending test email
            result = send_mail(
                'Test Email from Local Dev',
                'This is a test message.',
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

if __name__ == '__main__':
    test_smtp_connection()