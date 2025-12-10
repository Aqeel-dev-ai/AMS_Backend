import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_random_password(length=12):
    """
    Generate a secure random password.
    
    Args:
        length (int): Length of the password (default: 12)
    
    Returns:
        str: A random password containing uppercase, lowercase, digits, and special characters
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars),
    ]
    
    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def send_welcome_email(user_email, user_name, password):
    """
    Send a welcome email to a newly registered user with their login credentials.
    
    Args:
        user_email (str): The email address of the user
        user_name (str): The full name of the user
        password (str): The generated password for the user
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = 'Welcome to Attendance Management System - Your Login Credentials'
    
    # Create HTML message
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .credentials {{
                background-color: #f0f0f0;
                padding: 15px;
                border-left: 4px solid #4CAF50;
                margin: 20px 0;
            }}
            .credentials strong {{
                color: #4CAF50;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #777;
            }}
            .warning {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 10px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to AMS!</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user_name}</strong>,</p>
                
                <p>Your account has been created in the Attendance Management System. Below are your login credentials:</p>
                
                <div class="credentials">
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Password:</strong> {password}</p>
                </div>
                
                <div class="warning">
                    <p><strong>⚠️ Important Security Notice:</strong></p>
                    <p>Please change your password after your first login for security purposes. You can do this from your profile settings.</p>
                </div>
                
                <p>You can now log in to the system and start using all the features available to you.</p>
                
                <p>If you have any questions or need assistance, please don't hesitate to contact your administrator.</p>
                
                <p>Best regards,<br>
                <strong>Attendance Management System Team</strong></p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    plain_message = f"""
    Welcome to Attendance Management System!
    
    Hello {user_name},
    
    Your account has been created in the Attendance Management System. Below are your login credentials:
    
    Email: {user_email}
    Password: {password}
    
    ⚠️ IMPORTANT: Please change your password after your first login for security purposes.
    
    You can now log in to the system and start using all the features available to you.
    
    If you have any questions or need assistance, please don't hesitate to contact your administrator.
    
    Best regards,
    Attendance Management System Team
    
    ---
    This is an automated message. Please do not reply to this email.
    """
    try:
        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL, 
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False, 
        )
        if result == 1:
            print(f"Email successfully sent to {user_email}")
            return True
        else:
            print(f"Email failed (send_mail returned {result}) to {user_email}")
            return False

    except Exception as e:
        print(f"SMTP ERROR sending to {user_email}: {str(e)}")
        return False