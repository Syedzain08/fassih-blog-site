from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from json import loads
from zoneinfo import ZoneInfo
from db_models import Products


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
    created_at_local = order.created_at.astimezone(ZoneInfo("Asia/Karachi"))
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

    created_at_local = order.created_at.astimezone(ZoneInfo("Asia/Karachi"))
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

    created_at_local = order.created_at.astimezone(ZoneInfo("Asia/Karachi"))
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


def create_booking_confirmation_email(booking, recipient_email):
    """
    Creates a professional booking confirmation email for customers

    Args:
        booking (Bookings): The booking object containing all booking details
        recipient_email (str): Customer's email address

    Returns:
        MIMEMultipart: Formatted email message ready to send
    """
    created_at_local = booking.created_at.astimezone(ZoneInfo("Asia/Karachi"))
    formatted_created_date = created_at_local.strftime("%B %d, %Y at %I:%M %p")

    # Format the booking date and time
    booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
    formatted_booking_date = booking_datetime.strftime("%B %d, %Y")
    formatted_booking_time = booking_datetime.strftime("%I:%M %p")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ Booking Confirmed - {booking.service_type}"
    msg["From"] = "Vet Insights <blogs.fassih@gmail.com>"
    msg["To"] = recipient_email

    text_content = f"""
Hello {booking.first_name} {booking.last_name},

Great news! Your veterinary service booking has been confirmed.

BOOKING DETAILS:
Booking ID: {str(booking.id)}
Service: {booking.service_type}
{f"Animal: {booking.animal_type}" if booking.animal_type else ""}
Date: {formatted_booking_date}
Time: {formatted_booking_time}
Status: Confirmed

CONTACT INFORMATION:
Name: {booking.first_name} {booking.last_name}
Phone: {booking.phone}
Email: {booking.email}

{f"SPECIAL NOTES: {booking.notes}" if booking.notes else ""}

WHAT'S NEXT:
• Please arrive 10 minutes before your scheduled time
• Bring any relevant medical records for your animal
• If you need to reschedule, contact us at least 24 hours in advance

If you have any questions or need to make changes to your booking, please contact us at blogs.fassih@gmail.com or call us.

We look forward to seeing you soon!

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
            .header {{ text-align: center; margin-bottom: 30px; background-color: #e8f5e8; padding: 20px; border-radius: 8px; }}
            .booking-info {{ 
                background-color: #e8f5e8; 
                border: 2px solid #28a745; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 20px 0; 
            }}
            .booking-id {{ font-size: 18px; font-weight: bold; color: #28a745; }}
            .section {{ margin: 20px 0; }}
            .section-title {{ font-size: 16px; font-weight: bold; color: #2563eb; margin-bottom: 10px; }}
            .info-box {{ 
                background-color: #f8f9fa; 
                border-left: 4px solid #2563eb; 
                padding: 15px; 
                margin: 10px 0; 
            }}
            .important-box {{ 
                background-color: #fff9db; 
                border: 1px solid #fbbf24; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 20px 0; 
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
                <div class="success-icon">✅</div>
                <h1 style="color: #28a745; margin: 10px 0;">Booking Confirmed!</h1>
                <p>Your veterinary appointment is scheduled</p>
            </div>
            
            <div class="booking-info">
                <div class="booking-id">Booking ID: {str(booking.id)}</div>
                <p style="margin: 5px 0;"><strong>Service:</strong> {booking.service_type}</p>
                {f'<p style="margin: 5px 0;"><strong>Animal:</strong> {booking.animal_type}</p>' if booking.animal_type else ''}
                <p style="margin: 5px 0;"><strong>Date:</strong> {formatted_booking_date}</p>
                <p style="margin: 5px 0;"><strong>Time:</strong> {formatted_booking_time}</p>
                <p style="margin: 5px 0;">Status: <span style="color: #28a745; font-weight: bold;">Confirmed</span></p>
            </div>
            
            <div class="section">
                <div class="section-title">Contact Information</div>
                <div class="info-box">
                    <strong>{booking.first_name} {booking.last_name}</strong><br>
                    Phone: {booking.phone}<br>
                    Email: {booking.email}
                </div>
            </div>
            
            {f'<div class="section"><div class="section-title">Special Notes</div><p style="margin: 5px 0; font-style: italic;">{booking.notes}</p></div>' if booking.notes else ''}
            
            <div class="important-box">
                <h3 style="color: #92400e; margin: 0 0 10px 0;">📋 Before Your Visit:</h3>
                <ul style="margin: 0; color: #92400e;">
                    <li>Please arrive 10 minutes before your scheduled time</li>
                    <li>Bring any relevant medical records for your animal</li>
                    <li>Contact us at least 24 hours in advance for rescheduling</li>
                </ul>
            </div>
            
            <p>If you have any questions or need to make changes to your booking, please contact us at <a href="mailto:blogs.fassih@gmail.com">blogs.fassih@gmail.com</a>.</p>
            
            <p>We look forward to providing excellent care for your animal!</p>
            
            <p>Best regards,<br>
            <strong>Fassih Ul Abbas</strong><br>
            Vet Insights</p>
            
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


def create_booking_completion_email(booking, recipient_email):

    booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
    formatted_booking_date = booking_datetime.strftime("%B %d, %Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎉 Service Completed - {booking.service_type}"
    msg["From"] = "Vet Insights <blogs.fassih@gmail.com>"
    msg["To"] = recipient_email

    text_content = f"""
Hello {booking.first_name},

We hope you and your animal are doing well! Your veterinary service appointment has been successfully completed.

COMPLETED SERVICE:
Booking ID: {str(booking.id)[:8]}
Service: {booking.service_type}
Date: {formatted_booking_date}
Status: Completed

Thank you for choosing Vet Insights for your animal's healthcare needs. We were pleased to provide our services to you and your beloved companion.

FOLLOW-UP CARE:
If you have any questions about the treatment provided or need follow-up care, please don't hesitate to contact us at blogs.fassih@gmail.com.

We appreciate your trust in our services and look forward to serving you again in the future.

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
            .header {{ text-align: center; margin-bottom: 30px; background-color: #f0f8ff; padding: 20px; border-radius: 8px; }}
            .service-info {{ 
                background-color: #e8f5e8; 
                border: 2px solid #28a745; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 20px 0; 
            }}
            .follow-up-box {{ 
                background-color: #fff9db; 
                border: 1px solid #fbbf24; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 20px 0; 
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
                <div class="success-icon">🎉</div>
                <h1 style="color: #28a745; margin: 10px 0;">Service Completed!</h1>
                <p>Thank you for choosing Vet Insights</p>
            </div>
            
            <p>Hello {booking.first_name},</p>
            
            <p>We hope you and your animal are doing well! Your veterinary service appointment has been successfully <strong>completed</strong>.</p>
            
            <div class="service-info">
                <p style="margin: 5px 0;"><strong>Booking ID:</strong> {str(booking.id)[:8]}</p>
                <p style="margin: 5px 0;"><strong>Service:</strong> {booking.service_type}</p>
                <p style="margin: 5px 0;"><strong>Date:</strong> {formatted_booking_date}</p>
                <p style="margin: 5px 0;">Status: <span style="color: #28a745; font-weight: bold;">Completed</span></p>
            </div>
            
            <p>Thank you for choosing <strong>Vet Insights</strong> for your animal's healthcare needs. We were pleased to provide our services to you and your beloved companion.</p>
            
            <div class="follow-up-box">
                <h3 style="color: #92400e; margin: 0 0 10px 0;">🩺 Follow-up Care:</h3>
                <p style="margin: 0; color: #92400e;">
                    If you have any questions about the treatment provided or need follow-up care, please don't hesitate to contact us at <a href="mailto:blogs.fassih@gmail.com">blogs.fassih@gmail.com</a>.
                </p>
            </div>
            
            <p>We appreciate your trust in our services and look forward to serving you again in the future.</p>
            
            <p>Best regards,<br>
            <strong>Fassih Ul Abbas</strong><br>
            Vet Insights</p>
            
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


def create_booking_cancellation_email(booking, recipient_email, reason=None):

    booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
    formatted_booking_date = booking_datetime.strftime("%B %d, %Y")
    formatted_booking_time = booking_datetime.strftime("%I:%M %p")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"❌ Booking Cancelled - {booking.service_type}"
    msg["From"] = "Vet Insights <blogs.fassih@gmail.com>"
    msg["To"] = recipient_email

    text_content = f"""
Hello {booking.first_name} {booking.last_name},

We regret to inform you that your veterinary service booking has been cancelled.

CANCELLED BOOKING DETAILS:
Booking ID: {str(booking.id)[:8]}
Service: {booking.service_type}
{f"Animal: {booking.animal_type}" if booking.animal_type else ""}
Original Date: {formatted_booking_date}
Original Time: {formatted_booking_time}
Status: Cancelled

{f"REASON FOR CANCELLATION: {reason}" if reason else ""}

We sincerely apologize for any inconvenience this may cause. If you would like to reschedule your appointment, please contact us at blogs.fassih@gmail.com or call us to book a new appointment.

Our team is here to help ensure your animal receives the care they need at a time that works for you.

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
            .header {{ text-align: center; margin-bottom: 30px; background-color: #fee; padding: 20px; border-radius: 8px; }}
            .booking-info {{ 
                background-color: #fff0f0; 
                border: 2px solid #dc2626; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 20px 0; 
            }}
            .booking-id {{ font-size: 18px; font-weight: bold; color: #dc2626; }}
            .reason-box {{ 
                background-color: #fef3c7; 
                border: 1px solid #f59e0b; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 20px 0; 
            }}
            .reschedule-box {{ 
                background-color: #dbeafe; 
                border: 1px solid #3b82f6; 
                border-radius: 8px; 
                padding: 15px; 
                margin: 20px 0; 
            }}
            .footer {{ 
                margin-top: 30px; 
                padding-top: 20px; 
                border-top: 1px solid #eee; 
                font-size: 12px; 
                color: #666; 
                text-align: center; 
            }}
            .cancel-icon {{ color: #dc2626; font-size: 24px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="cancel-icon">❌</div>
                <h1 style="color: #dc2626; margin: 10px 0;">Booking Cancelled</h1>
                <p>We apologize for any inconvenience</p>
            </div>
            
            <p>Hello {booking.first_name} {booking.last_name},</p>
            
            <p>We regret to inform you that your veterinary service booking has been <strong>cancelled</strong>.</p>
            
            <div class="booking-info">
                <div class="booking-id">Booking ID: {str(booking.id)[:8]}</div>
                <p style="margin: 5px 0;"><strong>Service:</strong> {booking.service_type}</p>
                {f'<p style="margin: 5px 0;"><strong>Animal:</strong> {booking.animal_type}</p>' if booking.animal_type else ''}
                <p style="margin: 5px 0;"><strong>Original Date:</strong> {formatted_booking_date}</p>
                <p style="margin: 5px 0;"><strong>Original Time:</strong> {formatted_booking_time}</p>
                <p style="margin: 5px 0;">Status: <span style="color: #dc2626; font-weight: bold;">Cancelled</span></p>
            </div>
            
            {f'<div class="reason-box"><h3 style="color: #92400e; margin: 0 0 10px 0;">📝 Reason for Cancellation:</h3><p style="margin: 0; color: #92400e;">{reason}</p></div>' if reason else ''}
            
            <p>We sincerely apologize for any inconvenience this may cause.</p>
            
            <div class="reschedule-box">
                <h3 style="color: #1e40af; margin: 0 0 10px 0;">📅 Want to Reschedule?</h3>
                <p style="margin: 0; color: #1e40af;">
                    If you would like to book a new appointment, please contact us at <a href="mailto:blogs.fassih@gmail.com">blogs.fassih@gmail.com</a> or call us. Our team is here to help ensure your animal receives the care they need at a time that works for you.
                </p>
            </div>
            
            <p>Best regards,<br>
            <strong>Fassih Ul Abbas</strong><br>
            Vet Insights</p>
            
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


def create_admin_booking_alert_email(booking, admin_email, action_type="new"):

    action_icons = {
        "new": "🆕",
        "confirmed": "✅",
        "cancelled": "❌",
        "completed": "🎉",
    }

    action_colors = {
        "new": "#3b82f6",
        "confirmed": "#28a745",
        "cancelled": "#dc2626",
        "completed": "#8b5cf6",
    }

    created_at_local = booking.created_at.astimezone(ZoneInfo("Asia/Karachi"))
    formatted_created_date = created_at_local.strftime("%B %d, %Y at %I:%M %p")

    booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
    formatted_booking_date = booking_datetime.strftime("%B %d, %Y")
    formatted_booking_time = booking_datetime.strftime("%I:%M %p")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"[ADMIN] {action_icons.get(action_type, '📋')} Booking {action_type.title()} - {str(booking.id)[:8]}"
    )
    msg["From"] = "Vet Insights Booking System <blogs.fassih@gmail.com>"
    msg["To"] = admin_email

    text_content = f"""
BOOKING {action_type.upper()}

Booking ID: {booking.id}
Action: {action_type.title()}
Status: {booking.status.title()}
Created: {formatted_created_date}

SERVICE DETAILS:
Service Type: {booking.service_type}
{f"Animal Type: {booking.animal_type}" if booking.animal_type else ""}
Scheduled Date: {formatted_booking_date}
Scheduled Time: {formatted_booking_time}

CUSTOMER INFO:
Name: {booking.first_name} {booking.last_name}
Phone: {booking.phone}
Email: {booking.email}

{f"NOTES: {booking.notes}" if booking.notes else ""}

--
System generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
    """.strip()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                background-color: {action_colors.get(action_type, '#f8f9fa')}; 
                color: white; 
                padding: 15px; 
                border-radius: 8px; 
                text-align: center; 
                margin-bottom: 20px; 
            }}
            .booking-info {{ 
                background-color: #f8f9fa; 
                border-left: 4px solid {action_colors.get(action_type, '#6c757d')}; 
                padding: 15px; 
                margin: 15px 0; 
            }}
            .section {{ margin: 20px 0; }}
            .section-title {{ font-weight: bold; color: #2563eb; margin-bottom: 8px; }}
            .customer-info {{ 
                background-color: #e9ecef; 
                padding: 15px; 
                border-radius: 6px; 
                margin: 15px 0; 
            }}
            .footer {{ 
                margin-top: 30px; 
                padding-top: 15px; 
                border-top: 1px solid #dee2e6; 
                font-size: 12px; 
                color: #6c757d; 
                text-align: center; 
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin: 0;">{action_icons.get(action_type, '📋')} Booking {action_type.title()}</h2>
            </div>
            
            <div class="booking-info">
                <p style="margin: 5px 0;"><strong>Booking ID:</strong> {str(booking.id)}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> {booking.status.title()}</p>
                <p style="margin: 5px 0;"><strong>Created:</strong> {formatted_created_date}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Service Details</div>
                <p style="margin: 5px 0;"><strong>Service Type:</strong> {booking.service_type}</p>
                {f'<p style="margin: 5px 0;"><strong>Animal Type:</strong> {booking.animal_type}</p>' if booking.animal_type else ''}
                <p style="margin: 5px 0;"><strong>Scheduled Date:</strong> {formatted_booking_date}</p>
                <p style="margin: 5px 0;"><strong>Scheduled Time:</strong> {formatted_booking_time}</p>
            </div>
            
            <div class="section">
                <div class="section-title">Customer Information</div>
                <div class="customer-info">
                    <strong>{booking.first_name} {booking.last_name}</strong><br>
                    Phone: {booking.phone}<br>
                    Email: {booking.email}
                </div>
            </div>
            
            {f'<div class="section"><div class="section-title">Additional Notes</div><p style="font-style: italic; background-color: #fff3cd; padding: 10px; border-radius: 4px;">{booking.notes}</p></div>' if booking.notes else ''}
            
            <div class="footer">
                System generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
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
