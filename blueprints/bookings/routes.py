from flask import url_for, redirect, Blueprint, render_template, flash
from forms import NewBookingForm
from db_models import Bookings, db
from smtplib import SMTP
from os import getenv
from email_templates import create_admin_booking_alert_email


bookings_bp = Blueprint(
    "bookings", __name__, template_folder="templates", url_prefix="/bookings"
)


@bookings_bp.route("/new", methods=["GET", "POST"])
def new_booking():
    form = NewBookingForm()

    if form.validate_on_submit():

        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        phone_num = form.phone.data.strip()
        email = form.email.data.strip()
        service_type = form.service_type.data
        animal_type = form.animal_type.data.strip()
        additional_notes = form.notes.data.strip()
        prefered_date = form.booking_date.data
        prefered_time = form.start_time.data

        booking = Bookings(
            first_name=first_name,
            last_name=last_name,
            phone=phone_num,
            email=email,
            service_type=service_type,
            animal_type=animal_type,
            notes=additional_notes,
            booking_date=prefered_date,
            start_time=prefered_time,
        )

        try:
            db.session.add(booking)
            db.session.commit()
            flash(
                "Booking added. We'll get back to you to confirm the booking soon",
                "info",
            )

            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            password = getenv("GMAIL_APP_PASSWORD")
            user_address = getenv("GMAIL_ADDRESS")

            server.login(user_address, password)

            msg = create_admin_booking_alert_email(
                booking=booking, admin_email=getenv("SUPERADMIN_EMAIL")
            )

            server.sendmail(
                from_addr=user_address,
                to_addrs=getenv("SUPERADMIN_EMAIL"),
                msg=msg.as_bytes(),
            )

            server.quit()
            return redirect(url_for("index"))
        except Exception:
            db.session.rollback()
            flash("A Fatal Error Occured While Booking", "danger")
            return redirect(url_for("index"))

    return render_template("bookings/new_booking.html", form=form)
