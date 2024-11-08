import smtplib
import ssl
from dotenv import load_dotenv
import os
import uuid


def generate_unique_code():
    return str(uuid.uuid4())

def SendEmail(message,to):
    load_dotenv()
    our=os.getenv('EMAIL_HOST_USER')
    context = ssl._create_unverified_context()
    SMTP_SERVER=os.getenv('EMAIL_HOST')
    SMTP_PORT=os.getenv('EMAIL_PORT')
    PASSWORD=os.getenv('EMAIL_HOST_PASSWORD')
    full_message = f"Subject: your password as lambdatest vendor is\nFrom: {our}\nTo: {to}\n\n{message}"
    print(f"Email User: {our}")
    print(f"SMTP Server: {SMTP_SERVER}")
    print(f"SMTP Port: {SMTP_PORT}")    
    try:
        with smtplib.SMTP(SMTP_SERVER,int(SMTP_PORT)) as server:
            server.starttls(context=context)
            server.login(our,PASSWORD)
            server.sendmail(
                our,to,full_message
            )
    except Exception as e:
        print(f"Error sending email: {e}")

