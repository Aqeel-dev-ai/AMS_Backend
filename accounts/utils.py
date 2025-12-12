# utils.py
import secrets
import string
from django.core.mail import send_mail
from django.conf import settings

import secrets
import string

def generate_random_password():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "@#"

    # Ensure at least one of each type
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]

    all_chars = lowercase + uppercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(4)]

    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

def send_credentials_email(user_email, password):
    subject = "Your Account Credentials"
    message = f"""
Your account has been created.

Email: {user_email}
Password: {password}

Please log in and change your password immediately.

Thank you.
    """.strip()

    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        if result == 1:
            print(f"✓ Email successfully sent to {user_email}")
            return True
        else:
            print(f"⚠️ Email send returned {result} for {user_email}")
            return False
    except Exception as e:
        print(f"✗ Email failed for {user_email}: {e}")
        return False