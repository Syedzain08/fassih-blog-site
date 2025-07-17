# --- Standard Library Imports --- #
from io import BytesIO
from os import getenv, path

# --- Flask Core Imports --- #
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    Blueprint,
    redirect,
    url_for,
    send_from_directory,
)

# --- Flask Extensions --- #
from flask_login import LoginManager, login_required
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_mail import Mail
from flask_migrate import Migrate


# --- Third Party libraries --- #
from dotenv import load_dotenv
from cloudinary import config, uploader
from PIL import Image
from sqlalchemy import or_

# --- Local Application Imports --- #
from db_models import db, Admins, Articles, Products
from utils import *

# --- Blueprint Imports --- #
from blueprints.admin.routes import admin_bp
from blueprints.blog.routes import blog_bp
from blueprints.auth.routes import auth_bp
from blueprints.store.routes import store_bp
from blueprints.sitemap.sitemaps import sitemap_bp


# --- Enviroment Setup --- #
load_dotenv()

# --- App Creation --- #
app = Flask(__name__)


# --- Config --- #
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("SUPABASE_CONNECTION_STRING")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["WTF_CSRF_TIME_LIMIT"] = 3600
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 7200


# --- Extensions Initialization --- #
csrf = CSRFProtect(app)
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


# --- Register Blueprints --- #
app.register_blueprint(admin_bp)
app.register_blueprint(blog_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(store_bp)
app.register_blueprint(sitemap_bp)


# --- Cloudinary Config --- #
config(
    cloud_name=getenv("CLOUD_NAME"),
    api_key=getenv("CLOUDINARY_API_KEY"),
    api_secret=getenv("CLOUDINARY_API_SECRET"),
)


# --- User Loader --- #
@login_manager.user_loader
def load_user(user_id):
    return Admins.query.get(int(user_id))


# --- Public Routes --- #
@app.route("/", methods=["GET"])
def index():
    articles = (
        Articles.query.filter(Articles.status != "private")
        .order_by(Articles.created_at.desc())
        .all()
    )

    products = (
        (Products.query.filter(Products.in_stock != False))
        .order_by(Products.created_at.desc())
        .all()
    )
    for article in articles:
        if not article.description:
            article.description = extract_first_sentence(article.content)

    return render_template("index.html", articles=articles, products=products)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    tab = request.args.get("tab", "articles")
    page = request.args.get("page", 1, type=int)
    product_page = request.args.get("product_page", 1, type=int)

    articles_query = Articles.query.filter(
        Articles.status == "public",
        or_(
            Articles.title.ilike(f"%{query}%"),
            Articles.description.ilike(f"%{query}%"),
            Articles.content.ilike(f"%{query}%"),
            Articles.tags.ilike(f"%{query}%"),
            Articles.slug.ilike(f"%{query}%"),
        ),
    )

    article_pagination = articles_query.paginate(page=page, per_page=12)

    products_query = Products.query.filter(
        or_(
            Products.name.ilike(f"%{query}%"),
            Products.description.ilike(f"%{query}%"),
            Products.tags.ilike(f"%{query}%"),
            Products.slug.ilike(f"%{query}%"),
            Products.animal_type.ilike(f"%{query}%"),
            Products.form_type.ilike(f"%{query}%"),
        )
    )

    product_pagination = products_query.paginate(page=product_page, per_page=12)

    return render_template(
        "search_results.html",
        query=query,
        tab=tab,
        articles=article_pagination.items,
        article_pagination=article_pagination,
        products=product_pagination.items,
        product_pagination=product_pagination,
        active_tab=tab,
    )


# --- Authenticated Upload Routes --- #
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


# --- Redirects --- #
@app.route("/blog")
@app.route("/posts")
def blog_redirect():
    """Redirect common blog URLs to the main articles page"""
    return redirect(url_for("blog.all_articles"), code=301)


# --- Web Utiliyy --- #
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        path.join(app.root_path, "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


# --- Error Handlers --- #
@app.errorhandler(400)
def bad_request_error(error):
    return (
        render_template(
            "error.html",
            error_code=400,
            message="The request couldn't be understood. Please check your input.",
        ),
        400,
    )


@app.errorhandler(403)
def forbidden_error(error):
    return (
        render_template(
            "error.html",
            error_code=403,
            message="You don't have permission to access this resource.",
        ),
        403,
    )


@app.errorhandler(404)
def not_found_error(error):
    return (
        render_template(
            "error.html",
            error_code=404,
            message="The page you're looking for doesn't exist.",
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed_error(error):
    return (
        render_template(
            "error.html",
            error_code=405,
            message="The method you're using is not allowed for this endpoint.",
        ),
        405,
    )


@app.errorhandler(429)
def too_many_requests_error(error):
    return (
        render_template(
            "error.html",
            error_code=429,
            message="You're sending too many requests. Please slow down and try again.",
        ),
        429,
    )


@app.errorhandler(500)
def internal_error(error):
    return (
        render_template(
            "error.html",
            error_code=500,
            message="We're experiencing technical difficulties. Please try again later.",
        ),
        500,
    )


@app.errorhandler(CSRFError)
def csrf_error(error):
    return (
        render_template(
            "error.html",
            error_code=419,
            message="Your session has expired for security reasons. Please refresh and try again.",
        ),
        419,
    )


@app.errorhandler(Exception)
def handle_exception(error):
    return (
        render_template(
            "error.html",
            error_code=500,
            message="An unexpected error occurred. Please try again later.",
        ),
        500,
    )


# --- Run App --- #
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
