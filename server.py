from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    jsonify,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf import CSRFProtect
from flask_mail import Mail
from db_models import db, Admins, Articles
from forms import *
from sqlalchemy import func, or_, desc, asc
from smtplib import SMTP
from utils import *
from dotenv import load_dotenv
from os import getenv
from email_templates import *
from secrets import token_urlsafe
from datetime import datetime, timedelta
from cloudinary import config, uploader
from io import BytesIO
from PIL import Image
from flask_migrate import Migrate


load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("SUPABASE_CONNECTION_STRING")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

db.init_app(app)

migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


config(
    cloud_name=getenv("CLOUD_NAME"),
    api_key=getenv("CLOUDINARY_API_KEY"),
    api_secret=getenv("CLOUDINARY_API_SECRET"),
)


@login_manager.user_loader
def load_user(user_id):
    return Admins.query.get(int(user_id))


@app.route("/", methods=["GET"])
def index():
    articles = (
        Articles.query.filter(Articles.status != "private")
        .order_by(Articles.created_at.desc())
        .all()
    )
    for article in articles:
        if not article.description:
            article.description = extract_first_sentence(article.content)

    return render_template("index.html", articles=articles)


@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        user = Admins.query.filter_by(username=username).first()

        if user and check_password(password, user.password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/forgot-username", methods=["GET", "POST"])
def forgot_username():

    form = ForgotUsernameOrPassword()

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin_dashboard"))

    if form.validate_on_submit():
        email = form.email.data.lower()
        user = Admins.query.filter_by(email=email).first()

        if user:
            try:
                server = SMTP("smtp.gmail.com", 587)
                server.starttls()
                password = getenv("GMAIL_APP_PASSOWRD")
                user_address = getenv("GMAIL_ADDRESS")
                server.login(user_address, password)
                msg = create_username_recovery_email(user.username, email)
                server.sendmail(user_address, email, msg.as_string())
                flash(
                    "Email sent with your username. Please check your inbox.",
                    "info",
                )
                server.quit()
                return redirect(url_for("login"))
            except Exception:
                flash("A Fatal Error Occured While Sending Email:", "danger")
                return redirect(url_for("forgot_username"))
        else:
            flash("No user found with that email address.", "danger")
            return redirect(url_for("forgot_username"))

    return render_template("forgot_username.html", form=form)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotUsernameOrPassword()

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin_dashboard"))

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
                reset_link = url_for("reset_password", token=token, _external=True)
                msg = create_password_reset_email(
                    reset_link=reset_link, recipient_email=email
                )

                server = SMTP("smtp.gmail.com", 587)
                server.starttls()
                password = getenv("GMAIL_APP_PASSOWRD")
                user_address = getenv("GMAIL_ADDRESS")
                server.login(user_address, password)

                server.sendmail(user_address, email, msg.as_string())
                flash(
                    "Email sent with a password reset link. Please check your inbox.",
                    "info",
                )
                server.quit()

                return redirect(url_for("login"))

            except Exception:
                db.session.rollback()
                flash("A Fatal Error Occured While Sending Email", "danger")
                return redirect(url_for("forgot_password"))
        else:
            flash("No user found with that email address.", "danger")
            return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html", form=form)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()

    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("admin_dashboard"))

    users = Admins.query.filter(Admins.token_expiry > datetime.utcnow()).all()

    # Loop through and match the token
    user = next((u for u in users if check_password(token, u.token_store)), None)

    if not user:
        flash("Invalid or expired password reset token.", "danger")
        return redirect(url_for("forgot_password"))

    if user.token_expiry < datetime.utcnow():
        flash("Your password reset token has expired.", "danger")
        return redirect(url_for("forgot_password"))

    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password", token=token))

        if not check_password_criteria(new_password):
            flash(
                """
            <ul>Your password must contain:<ul/>
            <li>- At least 10 characters (and up to 100 characters)</li>
            <li>- At least 1 number</li>
            <li>- At least one lowercase and one uppercase character</li>
            <li>- Inclusion of at least one special character, e.g., ! @ # ?</li>
            """,
                "danger",
            )
            return redirect(url_for("reset_password", token=token))

        try:
            user.password = set_password(new_password)
            user.token_store = None
            user.token_expiry = None
            db.session.commit()
            flash("Your password has been reset successfully.", "success")
            return redirect(url_for("login"))
        except Exception:
            db.session.rollback()
            flash("A Fatal Error Occurred While Resetting Password:", "danger")
            return redirect(url_for("reset_password", token=token))

    return render_template("reset_password.html", form=form, token=token)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    total_articles = Articles.query.count()
    total_views = db.session.query(func.sum(Articles.view_count)).scalar() or 0
    return render_template(
        "admin/dashboard.html", total_articles=total_articles, total_views=total_views
    )


@app.route("/admin/manage_admins", methods=["GET", "POST"])
@login_required
def manage_admins():
    if not current_user.is_superadmin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("admin_dashboard"))

    admins = Admins.query.all()
    form = AddAdminForm()
    delete_form = DeleteAdminForm()

    return render_template(
        "admin/manage_admins.html", admins=admins, form=form, delete_form=delete_form
    )


@app.route("/admin/add/", methods=["POST"])
@login_required
def add_admin():
    if not current_user.is_superadmin:
        abort(403)

    form = AddAdminForm()

    if form.validate_on_submit():
        username = form.username.data.lower().strip()
        email = form.email.data.lower().strip()

        if not check_username_criteria(username):
            flash(
                "Username must be 3-25 characters long and cannot contain special characters.",
                "danger",
            )
            return redirect(url_for("manage_admins"))

    existing = Admins.query.filter(
        (Admins.username == username) | (Admins.email == email)
    ).first()
    if existing:
        flash("Admin with that username or email already exists.", "danger")
        return redirect(url_for("admin_dashboard"))

    new_admin = Admins(
        username=username,
        email=email,
        password="PlaceholderPasword",
        is_superadmin=False,
    )

    try:
        db.session.add(new_admin)
        db.session.commit()
        flash("New admin added successfully.", "success")
        return redirect(url_for("manage_admins"))
    except Exception:
        db.session.rollback()
        flash(f"A fatal error occured while trying to add a new admin", "danger")
        return redirect(url_for("manage_admins"))


@app.route("/admin/delete/", methods=["POST"])
@login_required
def delete_admin():
    if not current_user.is_superadmin:
        abort(403)

    form = DeleteAdminForm()

    if form.validate_on_submit():
        admin_id = form.admin_id.data
        admin_to_delete = Admins.query.get_or_404(admin_id)

        if admin_to_delete.is_superadmin:
            flash("You cannot delete the superadmin.", "danger")
            return redirect(url_for("manage_admins"))

        try:
            db.session.delete(admin_to_delete)
            db.session.commit()
            flash("Admin deleted successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while deleting the admin.", "danger")

    else:
        flash("Invalid deletion request.", "danger")

    return redirect(url_for("manage_admins"))


@app.route("/admin/add/posts", methods=["GET", "POST"])
@login_required
def add_post():

    form = BlogPostForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        thumbnail = request.form.get("thumbnail_link", "")
        content = form.content.data
        tags_raw = form.tags.data or ""
        tags = ",".join([t.strip() for t in tags_raw.split(",") if t.strip()])

        if not form.description.data:
            flash("Description is required.", "danger")
            return render_template(
                "admin/add_post.html",
                form=form,
                title=title,
                description=description,
                content=content,
                tags=tags,
                edit_mode=False,
            )

        if not form.content.data.strip():
            flash("Content is required.", "danger")
            return render_template(
                "admin/add_post.html",
                form=form,
                title=title,
                description=description,
                content=content,
                tags=tags,
                edit_mode=False,
            )

        try:
            slug = generate_unique_slug(title=title, model=Articles)

            new_article = Articles(
                title=title,
                description=description,
                slug=slug,
                thumbnail=thumbnail,
                content=content,
                author_id=current_user.id,
                tags=tags,
            )

            db.session.add(new_article)
            db.session.commit()
            flash("Article Created Successfully!", "success")
            return redirect(url_for("admin_dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(
                f"Something went terribly wrong while trying to add your post {e}",
                "danger",
            )
            return render_template(
                "admin/add_post.html",
                form=form,
                title=title,
                description=description,
                content=content,
                tags=tags,
                edit_mode=False,
            )

    return render_template("admin/add_post.html", form=form, edit_mode=False)


@app.route("/admin/edit/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    article = Articles.query.get_or_404(post_id)
    form = BlogPostForm(obj=article)

    if form.validate_on_submit():
        try:
            form.populate_obj(article)

            if "thumbnail_link" in request.form:
                article.thumbnail = request.form["thumbnail_link"]

            tags_raw = form.tags.data or ""
            article.tags = ",".join(
                [t.strip() for t in tags_raw.split(",") if t.strip()]
            )

            db.session.commit()
            flash("Article updated successfully!", "success")
            return redirect(url_for("admin_dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating article: {str(e)}", "danger")

    if article.tags:
        form.tags.data = article.tags

    return render_template(
        "admin/add_post.html", form=form, article=article, edit_mode=True
    )


@app.route("/articles/<int:article_id>/delete", methods=["POST", "GET"])
@login_required
def delete_article(article_id):

    article_to_delete = Articles.query.filter_by(id=article_id).first()

    if not article_to_delete:
        flash("Article doesn't exist", "error")
        return redirect(url_for("index"))

    try:
        db.session.delete(article_to_delete)
        db.session.commit()
        flash("Article deleted successfully", "success")
        return redirect(url_for("index"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting article: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/posts/<string:slug>", methods=["GET"])
def view_post(slug):
    try:

        article = Articles.query.filter_by(slug=slug).first()

        if not article:
            flash("Post not found", "danger")
            return redirect(url_for("index"))

        if article.status == "private" and not current_user.is_authenticated:
            flash("This post is private", "danger")
            return redirect(url_for("index"))

        if article.view_count is None:
            article.view_count = 1
        else:
            article.view_count += 1

        db.session.commit()

        related_posts = (
            Articles.query.filter(Articles.id != article.id)
            .order_by(Articles.created_at.desc())
            .limit(3)
            .all()
        )

        return render_template(
            "view_post.html", article=article, related_posts=related_posts
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error loading post: {e}", "danger")
        return redirect(url_for("index"))


@app.route("/admin/posts/manage", methods=["POST", "GET"])
@login_required
def manage_posts():
    articles = Articles.query.order_by(Articles.created_at.desc()).all()
    return render_template("admin/manage_posts.html", articles=articles)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 12

    if not query:

        articles = []
        pagination = None
        total_results = 0
    else:

        search_filter = or_(
            Articles.title.ilike(f"%{query}%"),
            Articles.description.ilike(f"%{query}%"),
            Articles.content.ilike(f"%{query}%"),
            Articles.tags.ilike(f"%{query}%"),
        )

        pagination = (
            Articles.query.filter(Articles.status == "public", search_filter)
            .order_by(Articles.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        articles = pagination.items
        total_results = pagination.total

    return render_template(
        "search_results.html",
        articles=articles,
        query=query,
        pagination=pagination,
        total_results=total_results,
    )


@app.route("/posts")
def all_posts():
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort", "newest")
    status_filter = request.args.get("status", "public")
    per_page = 12

    query = Articles.query

    # Handle status filtering
    if current_user.is_authenticated:
        if status_filter == "public":
            query = query.filter(Articles.status == "public")
        elif status_filter == "private":
            query = query.filter(Articles.status == "private")
        # If status_filter == "all", don't add any status filter (show all posts)
    else:
        # Non-authenticated users can only see public posts
        query = query.filter(Articles.status == "public")
        status_filter = "public"  # Force status to public for non-authenticated users

    # Handle sorting
    if sort_by == "newest":
        query = query.order_by(desc(Articles.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Articles.created_at))
    elif sort_by == "popular":
        query = query.order_by(desc(Articles.view_count))
    elif sort_by == "title_asc":
        query = query.order_by(asc(Articles.title))
    elif sort_by == "title_desc":
        query = query.order_by(desc(Articles.title))
    else:
        query = query.order_by(desc(Articles.created_at))

    total_articles = query.count()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    articles = pagination.items

    return render_template(
        "blog_page.html",
        articles=articles,
        pagination=pagination,
        total_articles=total_articles,
        current_sort=sort_by,
        current_status=status_filter,
    )


@app.route("/blog")
@app.route("/articles")
def blog_redirect():
    """Redirect common blog URLs to the main articles page"""
    return redirect(url_for("all_articles"), code=301)


@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    try:

        if "image" not in request.files:
            return jsonify({"success": False, "error": "No image uploaded"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"success": False, "error": "No selected file"}), 400

        if not allowed_image_file(file.filename):
            return (
                jsonify({"success": False, "error": "File Format Not Supported"}),
                400,
            )

        img = Image.open(file)

        img.thumbnail((1920, 1080), Image.LANCZOS)

        byte_stream = BytesIO()
        img.save(byte_stream, format="WEBP", quality=85)
        byte_stream.seek(0)

        upload_response = uploader.upload(byte_stream, format="webp")
        image_url = upload_response["secure_url"]

        return jsonify({"success": True, "link": image_url}), 200

    except Exception as e:
        app.logger.error(f"Image upload error: {str(e)}")
        return jsonify({"success": False, "error": f"Upload failed: {str(e)}"}), 500


@app.route("/upload_video", methods=["POST"])
@login_required
def upload_video():
    try:
        if "video" not in request.files:
            return jsonify({"success": False, "error": "No video uploaded"}), 400

        file = request.files["video"]

        if file.filename == "":
            return jsonify({"success": False, "error": "No selected file"}), 400

        if not allowed_video_file(file.filename):
            return (
                jsonify({"success": False, "error": "File Format Not Supported"}),
                400,
            )

        byte_stream = BytesIO(file.read())

        upload_response = uploader.upload(byte_stream, resource_type="video")
        video_url = upload_response["secure_url"]

        return jsonify({"success": True, "link": video_url}), 200

    except Exception as e:
        app.logger.error(f"Video upload error: {str(e)}")
        return jsonify({"success": False, "error": f"Upload failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
