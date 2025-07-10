# --- Standard Library Imports --- #
from io import BytesIO
from os import getenv

# --- Flask Core Imports --- #
from flask import Flask, render_template, request, jsonify, Blueprint

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
from db_models import db, Admins, Articles
from utils import *

# --- Blueprint Imports --- #
from blueprints.admin.routes import admin_bp
from blueprints.blog.routes import blog_bp
from blueprints.auth.routes import auth_bp


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


# --- Cloudinary Config --- #
config(
    cloud_name=getenv("CLOUD_NAME"),
    api_key=getenv("CLOUDINARY_API_KEY"),
    api_secret=getenv("CLOUDINARY_API_SECRET"),
)


# --- User Loader --- #
@login_manager.user_loader
def load_user(user_id):
    """
    Retrieves an Admin user instance by user ID for Flask-Login session management.
    
    Parameters:
        user_id (int or str): The unique identifier of the admin user.
    
    Returns:
        Admins or None: The Admin user object if found, otherwise None.
    """
    return Admins.query.get(int(user_id))


# --- Public Routes --- #
@app.route("/", methods=["GET"])
def index():
    """
    Render the homepage with a list of all public articles, ensuring each has a description.
    
    Articles without a description will have their description set to the first sentence of their content before rendering.
    """
    articles = (
        Articles.query.filter(Articles.status != "private")
        .order_by(Articles.created_at.desc())
        .all()
    )
    for article in articles:
        if not article.description:
            article.description = extract_first_sentence(article.content)

    return render_template("index.html", articles=articles)


@app.route("/search")
def search():
    """
    Handles article search requests by querying public articles matching the search term in title, description, content, or tags.
    
    If the query parameter is empty, returns an empty result set. Otherwise, performs a case-insensitive search, paginates results (12 per page), and renders the search results page with matching articles and pagination details.
    """
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


# --- Authenticated Upload Routes --- #
@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    """
    Handles authenticated image uploads, resizes and converts images to WEBP format, uploads them to Cloudinary, and returns the image URL in a JSON response.
    
    Returns:
        JSON response containing the upload status and, if successful, the URL of the uploaded image.
    """
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
    """
    Handles authenticated video file uploads, validates the file, uploads it to Cloudinary, and returns the video URL in a JSON response.
    
    Returns:
        Response: A JSON object indicating success and the uploaded video's URL, or an error message with the appropriate HTTP status code.
    """
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


# --- Error Handlers --- #
@app.errorhandler(400)
def bad_request_error(error):
    """
    Render a 400 Bad Request error page with a user-friendly message.
    
    Returns:
        A tuple containing the rendered error template and the HTTP 400 status code.
    """
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
    """
    Render a 403 Forbidden error page when a user attempts to access a resource without permission.
    
    Returns:
        A tuple containing the rendered error page and the HTTP 403 status code.
    """
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
    """
    Render a custom 404 error page when a requested resource is not found.
    
    Returns:
        A tuple containing the rendered error template and the HTTP 404 status code.
    """
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
    """
    Render a 405 error page when a request uses an unsupported HTTP method.
    
    Returns:
        A tuple containing the rendered error page and the HTTP 405 status code.
    """
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
    """
    Render a 429 error page when the user exceeds the allowed number of requests.
    
    Returns:
        A tuple containing the rendered error page and the HTTP status code 429.
    """
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
    """
    Handles HTTP 500 Internal Server Error by rendering a user-friendly error page.
    
    Returns:
        A tuple containing the rendered error template and the HTTP status code 500.
    """
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
    """
    Handle CSRF token errors by rendering a 419 error page indicating session expiration.
    """
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
    """
    Handles uncaught exceptions by rendering a generic 500 error page with a user-friendly message.
    
    Returns:
        A tuple containing the rendered error template and the HTTP 500 status code.
    """
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
