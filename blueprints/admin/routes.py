# --- Flask Core Imports --- #
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    Blueprint,
)

# --- Flask Extensions --- #
from flask_login import login_required, current_user
from sqlalchemy import func

# --- Local Application Imports --- #
from db_models import db, Admins, Articles
from forms import AddAdminForm, DeleteAdminForm, AddArticleForm
from utils import (
    check_username_criteria,
    generate_unique_slug,
    generate_throwaway_password,
)


# --- Admin Blueprint --- #
admin_bp = Blueprint(
    "admin",
    __name__,
    static_folder="static",
    template_folder="templates",
    url_prefix="/admin",
)


# --- Routes --- #
@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    """
    Render the admin dashboard with statistics on total articles and total article views.
    
    Returns:
        Rendered HTML template for the admin dashboard displaying article and view statistics.
    """
    total_articles = Articles.query.count()
    total_views = db.session.query(func.sum(Articles.view_count)).scalar() or 0
    return render_template(
        "admin/dashboard.html", total_articles=total_articles, total_views=total_views
    )


@admin_bp.route("/manage/admins", methods=["GET", "POST"])
@login_required
def manage_admins():
    """
    Render the admin management page for superadmins to view, add, or delete admin users.
    
    Redirects non-superadmin users to the admin dashboard with an error message.
    """
    if not current_user.is_superadmin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    admins = Admins.query.all()
    form = AddAdminForm()
    delete_form = DeleteAdminForm()

    return render_template(
        "admin/manage_admins.html", admins=admins, form=form, delete_form=delete_form
    )


@admin_bp.route("/add/admins", methods=["POST"])
@login_required
def add_admin():
    """
    Handles the creation of a new admin account by superadmins.
    
    Validates form input, checks for existing username or email, and creates a new admin with a generated temporary password. Only superadmins can access this route; unauthorized access results in a 403 error. Displays appropriate flash messages and redirects to the admin management page upon completion.
    """
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
            return redirect(url_for("admin.manage_admins"))

        existing = Admins.query.filter(
            (Admins.username == username) | (Admins.email == email)
        ).first()
        if existing:
            flash("Admin with that username or email already exists.", "danger")
            return redirect(url_for("admin.manage_admins"))

        throwaway_password = generate_throwaway_password()

        new_admin = Admins(
            username=username,
            email=email,
            password=throwaway_password,
            is_superadmin=False,
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash("New admin added successfully.", "success")
            return redirect(url_for("admin.manage_admins"))
        except Exception:
            db.session.rollback()
            flash(f"A fatal error occurred while trying to add a new admin", "danger")
            return redirect(url_for("admin.manage_admins"))
    flash("Form submission failed. Please check your input.", "danger")

    return redirect(url_for("admin.manage_admins"))


@admin_bp.route("/delete/admin", methods=["POST"])
@login_required
def delete_admin():
    """
    Deletes an admin account based on form submission, preventing deletion of the superadmin.
    
    Redirects to the admin management page with a success or error message depending on the outcome.
    """
    if not current_user.is_superadmin:
        abort(403)

    form = DeleteAdminForm()

    if form.validate_on_submit():
        admin_id = form.admin_id.data
        admin_to_delete = Admins.query.get_or_404(admin_id)

        if admin_to_delete.is_superadmin:
            flash("You cannot delete the superadmin.", "danger")
            return redirect(url_for("admin.manage_admins"))

        try:
            db.session.delete(admin_to_delete)
            db.session.commit()
            flash("Admin deleted successfully.", "success")
        except Exception:
            db.session.rollback()
            flash("An error occurred while deleting the admin.", "danger")

    else:
        flash("Invalid deletion request.", "danger")

    return redirect(url_for("admin.manage_admins"))


@admin_bp.route("/add/article", methods=["GET", "POST"])
@login_required
def add_article():

    """
    Handles the creation of a new article by processing form input, generating a unique slug, and saving the article to the database.
    
    On successful submission, redirects to the admin dashboard with a success message. If an error occurs during database operations, rolls back the transaction and re-renders the article creation form with an error message.
    """
    form = AddArticleForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        thumbnail = request.form.get("thumbnail_link", "")
        content = form.content.data
        tags_raw = form.tags.data or ""
        tags = ",".join([t.strip() for t in tags_raw.split(",") if t.strip()])

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
            return redirect(url_for("admin.admin_dashboard"))

        except Exception:
            db.session.rollback()
            flash(
                f"Something went terribly wrong while trying to add your article",
                "danger",
            )
            return render_template(
                "admin/add_article.html",
                form=form,
                title=title,
                description=description,
                content=content,
                tags=tags,
                edit_mode=False,
            )

    return render_template("admin/add_article.html", form=form, edit_mode=False)


@admin_bp.route("/edit/article/<int:article_id>", methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    """
    Edit an existing article by updating its details and tags.
    
    Parameters:
        article_id (int): The ID of the article to edit.
    
    Returns:
        Response: Renders the article editing form on GET or failed submission, or redirects to the admin dashboard on successful update.
    """
    article = Articles.query.get_or_404(article_id)
    form = AddArticleForm(obj=article)

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
            return redirect(url_for("admin.admin_dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating article: {str(e)}", "danger")

    if article.tags:
        form.tags.data = article.tags

    return render_template(
        "admin/add_article.html", form=form, article=article, edit_mode=True
    )


@admin_bp.route("/manage/articles", methods=["POST", "GET"])
@login_required
def manage_articles():
    """
    Render the admin page displaying a list of all articles ordered by creation date (newest first).
    """
    articles = Articles.query.order_by(Articles.created_at.desc()).all()
    return render_template("admin/manage_articles.html", articles=articles)


@admin_bp.route("/articles/<int:article_id>/delete", methods=["POST"])
@login_required
def delete_article(article_id):

    """
    Deletes an article by its ID if it exists.
    
    If the article does not exist, flashes an error message and redirects to the articles management page. On successful deletion, flashes a success message; on failure, rolls back the transaction, flashes an error message, and redirects to the articles management page.
    """
    article_to_delete = Articles.query.filter_by(id=article_id).first()

    if not article_to_delete:
        flash("Article doesn't exist", "danger")
        return redirect(url_for("admin.manage_articles"))

    try:
        db.session.delete(article_to_delete)
        db.session.commit()
        flash("Article deleted successfully", "success")
        return redirect(url_for("admin.manage_articles"))
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting article: {str(e)}", "error")
        return redirect(url_for("admin.manage_articles"))
