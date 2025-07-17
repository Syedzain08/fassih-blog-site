from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from json import loads
from db_models import Products
from pytz import timezone


karachi_tz = timezone("Asia/Karachi")


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
    msg["From"] = "Fassih Ul Abbas <blogs.fassih@gmail.com>"
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
    msg["From"] = "Fassih Ul Abbas <blogs.fassih@gmail.com>"
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


def create_order_confirmation_email(order, recipient_email):
    """
    Creates a professional order confirmation email for customers

    Args:
        order (Orders): The order object containing all order details
        recipient_email (str): Customer's email address

    Returns:
        MIMEMultipart: Formatted email message ready to send
    """

    created_at_local = order.created_at.astimezone(karachi_tz)
    formatted_date = created_at_local.strftime("%B %d, %Y at %I:%M %p")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Order Confirmation #{str(order.id)[:8]} "
    msg["From"] = "Fassih Ul Abbas <blogs.fassih@gmail.com>"
    msg["To"] = recipient_email

    items_text = ""
    items_html = ""

    for item in order.items:
        variant_info = ""
        if item.variant_data and item.variant_data != "{}":
            try:
                variants = loads(item.variant_data)
                matched_product = Products.query.get(item.product_id)

                variant_lines = []
                for name, value in variants.items():
                    matched_variant = next(
                        (
                            v
                            for v in matched_product.variants
                            if v.variant_name == name and v.variant_value == value
                        ),
                        None,
                    )
                    if matched_variant:
                        extra = (
                            f" (+PKR {float(matched_variant.price):.0f})"
                            if float(matched_variant.price) > 0
                            else ""
                        )
                        variant_lines.append(f"{name}: {value}{extra}")
                    else:
                        variant_lines.append(f"{name}: {value}")

                variant_info = " (" + ", ".join(variant_lines) + ")"
            except:
                variant_info = ""

        items_text += f"• {item.product_name}{variant_info}\n  Quantity: {item.quantity} × PKR {item.unit_price} = PKR {item.total_price}\n\n"

        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">
                <strong>{item.product_name}</strong>{variant_info}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">
                {item.quantity}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">
                PKR {item.unit_price}
            </td>
            <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">
                <strong>PKR {item.total_price}</strong>
            </td>
        </tr>
        """

    text_content = f"""
Hello {order.first_name} {order.last_name},

Thank you for your order! We've received your order and it's being processed.

ORDER DETAILS:
Order ID: {order.id}
Order Date: {formatted_date}
Status: {order.status.title()}

ITEMS ORDERED:
{items_text}

TOTAL: PKR {order.total_amount}

SHIPPING ADDRESS:
{order.first_name} {order.last_name}
{order.street_address}
{order.sub_area}, {order.area}
Phone: {order.phone}

PAYMENT METHOD: {order.payment_method.replace('_', ' ').title()}

{f"ADDITIONAL NOTES: {order.additional_notes}" if order.additional_notes else ""}

If you have any questions about your order, please contact us at blogs.fassih@gmail.com or reply to this email.

Thank you for choosing Vet Insights!

Best regards,
Fassih Ul Abbas
Vet Insights

--
This email was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    """.strip()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
            .order-info {{ 
                background-color: #e8f5e8; 
                border: 2px solid #28a745; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 20px 0; 
            }}
            .order-id {{ font-size: 18px; font-weight: bold; color: #28a745; }}
            .section {{ margin: 20px 0; }}
            .section-title {{ font-size: 16px; font-weight: bold; color: #2563eb; margin-bottom: 10px; }}
            .items-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            .items-table th {{ background-color: #f8f9fa; padding: 10px; text-align: left; border-bottom: 2px solid #dee2e6; }}
            .total-row {{ background-color: #f8f9fa; font-weight: bold; }}
            .address-box {{ 
                background-color: #f8f9fa; 
                border-left: 4px solid #2563eb; 
                padding: 15px; 
                margin: 10px 0; 
            }}
            .footer {{ 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #eee; 
                font-size: 12px; 
                color: #666; 
                text-align: center; 
            }}
            .success-icon {{ color: #28a745; font-size: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="success-icon">✓</div>
                <h1 style="color: #28a745; margin: 10px 0;">Order Confirmed!</h1>
                <p>Thank you for your order, {order.first_name}!</p>
            </div>
            
            <div class="order-info">
                <div class="order-id">Order ID: {str(order.id)}</div>
                <p style="margin: 5px 0;">Date: {formatted_date}</p>
                <p style="margin: 5px 0;">Status: <span style="color: #28a745; font-weight: bold;">{order.status.title()}</span></p>
            </div>
            
            <div class="section">
                <div class="section-title">Items Ordered</div>
                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Price</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                        <tr class="total-row">
                            <td colspan="3" style="padding: 12px; text-align: right;">
                                <strong>Total Amount:</strong>
                            </td>
                            <td style="padding: 12px; text-align: right;">
                                <strong>PKR {order.total_amount}</strong>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">Shipping Address</div>
                <div class="address-box">
                    <strong>{order.first_name} {order.last_name}</strong><br>
                    {order.street_address}<br>
                    {order.sub_area}, {order.area}<br>
                    Phone: {order.phone}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Payment Method</div>
                <p style="margin: 5px 0;"><strong>{order.payment_method.replace('_', ' ').title()}</strong></p>
            </div>
            
            {f'<div class="section"><div class="section-title">Additional Notes</div><p style="margin: 5px 0; font-style: italic;">{order.additional_notes}</p></div>' if order.additional_notes else ''}
            
            <div style="background-color: #fff9db; border: 1px solid #fbbf24; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <h3 style="color: #92400e; margin: 0 0 10px 0;">What's Next?</h3>
                <p style="margin: 0; color: #92400e;">
                    Our team will contact you shortly to confirm your order and arrange delivery.
                </p>
            </div>
            
            <p>If you have any questions about your order, please contact us at <a href="mailto:blogs.fassih@gmail.com">blogs.fassih@gmail.com</a> or reply to this email.</p>
            
            
            
            <p>Best regards,<br>
            <strong>Fassih Ul Abbas</strong><br>
            </p>
            
            <div class="footer">
                This email was sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>
    </body>
    </html>
    """

    # Attach both versions
    part1 = MIMEText(text_content, "plain", "utf-8")
    part2 = MIMEText(html_content, "html", "utf-8")

    msg.attach(part1)
    msg.attach(part2)

    return msg


def create_admin_order_alert_email(order, admin_email):
    """
    Creates a simplified order summary email for the admin

    Args:
        order (Orders): The order object containing all order details
        admin_email (str): Admin recipient email

    Returns:
        MIMEMultipart: Email ready to be sent
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[ADMIN] New Order #{str(order.id)[:8]}"
    msg["From"] = "Vet Insights Order System <blogs.fassih@gmail.com>"
    msg["To"] = admin_email

    created_at_local = order.created_at.astimezone(karachi_tz)
    formatted_date = created_at_local.strftime("%B %d, %Y at %I:%M %p")

    items_html = ""
    for item in order.items:
        variant_info = ""
        if item.variant_data and item.variant_data != "{}":
            try:
                variants = loads(item.variant_data)
                lines = [f"{k}: {v}" for k, v in variants.items()]
                variant_info = (
                    "<br><small><em>Variants: " + ", ".join(lines) + "</em></small>"
                )
            except:
                pass

        items_html += f"""
        <tr>
            <td style="padding: 6px; border-bottom: 1px solid #ddd;">
                <strong>{item.product_name}</strong>{variant_info}
            </td>
            <td style="text-align:center; padding: 6px; border-bottom: 1px solid #ddd;">
                {item.quantity}
            </td>
            <td style="text-align:right; padding: 6px; border-bottom: 1px solid #ddd;">
                Rs. {item.unit_price:.0f}
            </td>
            <td style="text-align:right; padding: 6px; border-bottom: 1px solid #ddd;">
                <strong>Rs. {item.total_price:.0f}</strong>
            </td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; }}
            .table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .table th {{ background-color: #f3f3f3; padding: 8px; border-bottom: 2px solid #ccc; }}
            .section-title {{ margin-top: 20px; font-weight: bold; color: #2563eb; }}
        </style>
    </head>
    <body>
        <h2>🚨 New Order Received</h2>
        <p><strong>Order ID:</strong> {str(order.id)}<br>
           <strong>Order Time:</strong> {formatted_date}<br>
           <strong>Source:</strong> {order.source.title()}<br>
           <strong>Status:</strong> {order.status.title()}</p>

        <div class="section-title">Customer Info</div>
        <p>
            <strong>{order.first_name} {order.last_name}</strong><br>
            {order.street_address}, {order.sub_area}, {order.area}<br>
            Phone: {order.phone}<br>
            Email: {order.email}
        </p>

        <div class="section-title">Order Items</div>
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Qty</th>
                    <th style="text-align:right;">Price</th>
                    <th style="text-align:right;">Total</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
                <tr style="background-color: #f8f9fa;">
                    <td colspan="3" style="text-align: right; padding: 10px;"><strong>Total:</strong></td>
                    <td style="text-align: right; padding: 10px;"><strong>Rs. {order.total_amount:.0f}</strong></td>
                </tr>
            </tbody>
        </table>

        <div class="section-title">Payment Method</div>
        <p>{order.payment_method.replace("_", " ").title()}</p>

        {"<div class='section-title'>Additional Notes</div><p style='font-style: italic;'>" + order.additional_notes + "</p>" if order.additional_notes else ""}

        <hr>
        <p style="font-size: 12px; color: #888;">System generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </body>
    </html>
    """

    text = f"""
New Order Received

Order ID: {order.id}
Order Time: {formatted_date}
Source: {order.source.title()}
Status: {order.status.title()}

Customer:
{order.first_name} {order.last_name}
{order.street_address}, {order.sub_area}, {order.area}
Phone: {order.phone}
Email: {order.email}

Items:
"""

    for item in order.items:
        text += f"- {item.product_name} (x{item.quantity}) @ Rs. {item.unit_price:.0f} = Rs. {item.total_price:.0f}\n"
        if item.variant_data and item.variant_data != "{}":
            try:
                variants = loads(item.variant_data)
                for k, v in variants.items():
                    text += f"  • {k}: {v}\n"
            except:
                pass
    text += f"\nTotal: Rs. {order.total_amount:.0f}\n"
    text += f"Payment Method: {order.payment_method.replace('_', ' ').title()}\n"
    if order.additional_notes:
        text += f"Notes: {order.additional_notes}\n"
    text += f"\n--\nGenerated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"

    # Attach both versions
    part1 = MIMEText(text, "plain", "utf-8")
    part2 = MIMEText(html, "html", "utf-8")
    msg.attach(part1)
    msg.attach(part2)

    return msg


def create_order_completion_email(order, recipient_email):

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎉 Order #{str(order.id)[:8]} Completed!"
    msg["From"] = "Vet Insights <blogs.fassih@gmail.com>"
    msg["To"] = recipient_email

    created_at_local = order.created_at.astimezone(karachi_tz)
    formatted_date = created_at_local.strftime("%B %d, %Y at %I:%M %p")

    text = f"""
Hi {order.first_name},

Good news! Your order #{order.id} has been successfully completed and delivered.

Order Summary:
Date: {formatted_date}
Total Paid: PKR {order.total_amount}

Thank you for shopping with Vet Insights. We hope to see you again soon!

Best regards,
Fassih Ul Abbas
Vet Insights
    """.strip()

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #28a745;">🎉 Your Order is Complete!</h2>
            <p>Hi {order.first_name},</p>
            <p>We're excited to let you know that your order <strong>#{order.id}</strong> has been successfully <strong>delivered</strong>.</p>

            <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
                <tr>
                    <td><strong>Order Date:</strong></td>
                    <td>{formatted_date}</td>
                </tr>
                <tr>
                    <td><strong>Total Paid:</strong></td>
                    <td>PKR {order.total_amount}</td>
                </tr>
            </table>

            <p>Thank you for choosing <strong>Vet Insights</strong>. We look forward to serving you again!</p>
            <p>Warm regards,<br>Fassih Ul Abbas<br><em>Vet Insights</em></p>
            <hr style="margin-top: 40px;">
            <p style="font-size: 12px; color: #888;">Sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def create_order_cancellation_email(order, recipient_email, reason=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"❌ Order #{str(order.id)[:8]} Cancelled"
    msg["From"] = "Vet Insights <blogs.fassih@gmail.com>"
    msg["To"] = recipient_email

    # Construct plain text
    text = f"""
Hi {order.first_name},

We regret to inform you that your order #{order.id} has been cancelled.
""".strip()

    if reason:
        text += f"\n\nReason: {reason}"

    text += """
\nIf you have any questions or would like to place a new order, feel free to contact us at blogs.fassih@gmail.com.

Best regards,
Vet Insights
""".strip()

    # Construct HTML
    html_reason = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""

    html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #dc2626;">❌ Order Cancelled</h2>
        <p>Dear {order.first_name},</p>
        <p>We're sorry to let you know that your order <strong>#{order.id}</strong> has been <strong>cancelled</strong>.</p>
        {f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""}
        <p>If you have any concerns or would like to reorder, please get in touch at <a href="mailto:blogs.fassih@gmail.com">blogs.fassih@gmail.com</a>.</p>
        <p>Best regards,<br>Fassih Ul Abbas<br><em>Vet Insights</em></p>
        <hr style="margin-top: 40px;">
        <p style="font-size: 12px; color: #888;">Sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>
</body>
</html>
    """

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg
