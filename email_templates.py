# email_templates.py

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def create_username_recovery_email(username, recipient_email):
    """
    Creates a professional username recovery email for the blog admin

    Args:
        username (str): The user's username
        recipient_email (str): Email address to send to

    Returns:
        MIMEMultipart: Formatted email message ready to send
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Username Recovery - Admin Dashboard"
    msg["From"] = "Fassih Ul Abbas <contact.fassihabbas@gmail.com>"
    msg["To"] = recipient_email

    text_content = f"""
Hello,

You requested to recover your username for the admin dashboard.

Your username is: {username}

You can now use this username to log into your dashboard.

If you did not request this, please ignore this email.

Best regards,
Fassih Ul Abbas

--
This email was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    """.strip()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .username-box {{ 
                background-color: #f0f8ff; 
                border: 2px solid #2563eb; 
                border-radius: 8px; 
                padding: 20px; 
                text-align: center; 
                margin: 20px 0; 
            }}
            .username {{ font-size: 18px; font-weight: bold; color: #2563eb; }}
            .footer {{ 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #eee; 
                font-size: 12px; 
                color: #666; 
                text-align: center; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Username Recovery</h2>
            </div>
            
            <p>Hello,</p>
            
            <p>You requested to recover your username for the admin dashboard.</p>
            
            <div class="username-box">
                <div class="username">Your username is: {username}</div>
            </div>
            
            <p>You can now use this username to log into your dashboard.</p>
            
            <p>If you did not request this, please ignore this email.</p>
            
            <p>Best regards,<br>
            <strong>Fassih Ul Abbas</strong></p>
            
            <div class="footer">
                This email was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>
    </body>
    </html>
    """

    # Attach both versions
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")

    msg.attach(part1)
    msg.attach(part2)

    return msg


def create_password_reset_email(reset_link, recipient_email):
    """
    Creates a professional password reset email for the blog admin

    Args:
        reset_token (str): The password reset token
        recipient_email (str): Email address to send to

    Returns:
        MIMEMultipart: Formatted email message ready to send
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset Request - Admin Dashboard"
    msg["From"] = "Fassih Ul Abbas <contact.fassihabbas@gmail.com>"
    msg["To"] = recipient_email

    text_content = f"""
Hello,

You requested to reset your password for the admin dashboard.

Your password reset token is: {reset_link}

Please enter this token on the password reset page to set a new password.

This token will expire in 15 minutes.

If you did not request a password reset, please ignore this email.

Best regards,
Fassih Ul Abbas

--
This email was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    """.strip()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .token-box {{ 
                background-color: #fff0f0; 
                border: 2px solid #dc2626; 
                border-radius: 8px; 
                padding: 20px; 
                text-align: center; 
                margin: 20px 0; 
                font-family: monospace;
            }}
            .token {{ font-size: 18px; font-weight: bold; color: #dc2626; }}
            .highlight {{ 
                background-color: #fff9db;
                padding: 3px 6px;
                border-radius: 4px;
                font-weight: bold;
            }}
            .footer {{ 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #eee; 
                font-size: 12px; 
                color: #666; 
                text-align: center; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Password Reset Request</h2>
            </div>
            
            <p>Hello,</p>
            
            <p>You requested to reset your password for the admin dashboard.</p>
            
            <div class="token-box">
                <div class="token">Your reset token: {reset_link}</div>
            </div>
            
            <p>Please enter this token on the password reset page to set a new password.</p>
            
            <p><span class="highlight">Important:</span> This token will expire in 15 minutes.</p>
            
            <p>If you did not request a password reset, please ignore this email.</p>
            
            <p>Best regards,<br>
            <strong>Fassih Ul Abbas</strong></p>
            
            <div class="footer">
                This email was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>
    </body>
    </html>
    """

    # Attach both versions
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")

    msg.attach(part1)
    msg.attach(part2)

    return msg
