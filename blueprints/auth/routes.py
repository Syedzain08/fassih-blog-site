# --- Standard Library Imports --- #
from datetime import datetime, timedelta
from os import getenv
from secrets import token_urlsafe
from smtplib import SMTP

# --- Flask Core Imports --- #
from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from markupsafe import Markup


# --- Local Application Imports --- #
from db_models import Admins, db
from forms import LoginForm, ForgotUsernameOrPassword, ResetPasswordForm
from utils import set_password, check_password_criteria, check_password
from email_templates import create_username_recovery_email, create_password_reset_email

# --- Auth Blueprint --- #
auth_bp = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")


# --- Routes --- #
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin.admin_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        user = Admins.query.filter_by(username=username).first()

        if user and check_password(password, user.password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-username", methods=["GET", "POST"])
def forgot_username():

    form = ForgotUsernameOrPassword()

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin.admin_dashboard"))

    if form.validate_on_submit():
        email = form.email.data.lower()
        user = Admins.query.filter_by(email=email).first()

        if user:
            try:
                server = SMTP("smtp.gmail.com", 587)
                server.starttls()
                password = getenv("GMAIL_APP_PASSWORD")
                user_address = getenv("GMAIL_ADDRESS")
                server.login(user_address, password)
                msg = create_username_recovery_email(user.username, email)
                server.sendmail(user_address, email, msg.as_string())
                flash(
                    "Email sent with your username. Please check your inbox.",
                    "info",
                )
                server.quit()
                return redirect(url_for("auth.login"))
            except Exception:
                flash("A Fatal Error Occured While Sending Email:", "danger")
                return redirect(url_for("auth.forgot_username"))
        else:
            flash("No user found with that email address.", "danger")
            return redirect(url_for("auth.forgot_username"))

    return render_template("auth/forgot_username.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotUsernameOrPassword()

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin.admin_dashboard"))

    if form.validate_on_submit():
        email = form.email.data.lower()
        user = Admins.query.filter_by(email=email).first()

        if user:
            token = token_urlsafe(32)
            token_hash = set_password(token)
            user.token_store = token_hash
            user.token_expiry = datetime.utcnow() + timedelta(minutes=15)
            try:
                db.session.commit()
                reset_link = url_for("auth.reset_password", token=token, _external=True)
                msg = create_password_reset_email(
                    reset_link=reset_link, recipient_email=email
                )

                server = SMTP("smtp.gmail.com", 587)
                server.starttls()
                password = getenv("GMAIL_APP_PASSWORD")
                user_address = getenv("GMAIL_ADDRESS")
                server.login(user_address, password)

                server.sendmail(user_address, email, msg.as_string())
                flash(
                    "Email sent with a password reset link. Please check your inbox.",
                    "info",
                )
                server.quit()

                return redirect(url_for("auth.login"))

            except Exception:
                db.session.rollback()
                flash("A Fatal Error Occured While Sending Email", "danger")
                return redirect(url_for("auth.forgot_password"))
        else:
            flash("No user found with that email address.", "danger")
            return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin.admin_dashboard"))

    users = Admins.query.filter(Admins.token_expiry > datetime.utcnow()).all()

    user = next((u for u in users if check_password(token, u.token_store)), None)

    if not user:
        flash("Invalid or expired password reset token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if user.token_expiry < datetime.utcnow():
        flash("Your password reset token has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        if not check_password_criteria(new_password):
            flash(
                Markup(
                    """
            <ul>Your password must contain:<ul/>
            <li>- At least 10 characters (and up to 100 characters)</li>
            <li>- At least 1 number</li>
            <li>- At least one lowercase and one uppercase character</li>
            <li>- Inclusion of at least one special character, e.g., ! @ # ?</li>
            """
                ),
                "danger",
            )
            return redirect(url_for("auth.reset_password", token=token))

        try:
            user.password = set_password(new_password)
            user.token_store = None
            user.token_expiry = None
            db.session.commit()
            flash("Your password has been reset successfully.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("A Fatal Error Occurred While Resetting Password:", "danger")
            return redirect(url_for("auth.reset_password", token=token))

    return render_template("auth/reset_password.html", form=form, token=token)
