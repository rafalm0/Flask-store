import os
import requests
from dotenv import load_dotenv

if os.path.exists("env_config.py"):
    import env_config

load_dotenv()


def send_simple_message(to, subject, body):
    load_dotenv()
    if os.path.exists("env_config.py"):
        domain = env_config.MAILGUN_DOMAIN
        key = env_config.MAILGUN_API_KEY
    else:
        domain = os.getenv("MAILGUN_DOMAIN")
        key = os.getenv("MAILGUN_API_KEY")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", f"{key}"),
        data={"from": f"Mail User <mailgun@{domain}>",
              "to": [to],
              "subject": subject,
              "text": body})


def send_user_registration_email(email, username):
    return send_simple_message(to=email, subject="Signup", body=f"Successfully signed up. {username}")
