# --- Flask Core Imports --- #
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

# --- Flask Extensions --- #

from flask_login import current_user
from sqlalchemy import desc, asc

# --- Local Application Imports --- #

from db_models import Articles, db

# --- Blog Blueprint --- #
blog_bp = Blueprint(
    "blog", __name__, template_folder="templates", url_prefix="/articles"
)


# --- Routes --- #


@blog_bp.route("/")
def all_articles():
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort", "newest")
    status_filter = request.args.get("status", "public")
    per_page = 12

    query = Articles.query

    if current_user.is_authenticated:
        if status_filter == "public":
            query = query.filter(Articles.status == "public")
        elif status_filter == "private":
            query = query.filter(Articles.status == "private")

    else:

        query = query.filter(Articles.status == "public")
        status_filter = "public"

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
        "blog/blog_page.html",
        articles=articles,
        pagination=pagination,
        total_articles=total_articles,
        current_sort=sort_by,
        current_status=status_filter,
    )


@blog_bp.route("/<string:slug>", methods=["GET"])
def view_article(slug):
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
            Articles.query.filter(
                Articles.id != article.id,
                (
                    Articles.status == "public"
                    if not current_user.is_authenticated
                    else True
                ),
            )
            .order_by(Articles.created_at.desc())
            .limit(3)
            .all()
        )

        return render_template(
            "blog/view_article.html", article=article, related_posts=related_posts
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Error loading post: {e}", "danger")
        return redirect(url_for("index"))
