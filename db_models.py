from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin


db = SQLAlchemy()


class Admins(db.Model, UserMixin):
    __tablename__ = "Admins"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    token_store = db.Column(db.String, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    is_superadmin = db.Column(db.Boolean, default=False, nullable=False)

    articles = db.relationship("Articles", back_populates="author")

    def __init__(self, username, password, email, is_superadmin=False):
        self.username = username
        self.password = password
        self.email = email
        self.token_store = None
        self.token_expiry = None
        self.is_superadmin = is_superadmin


class Articles(db.Model):
    __tablename__ = "Articles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("Admins.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(
        db.Enum("public", "private", name="article_status_enum"),
        default="public",
        nullable=False,
    )

    # Analytics
    view_count = db.Column(db.Integer, default=0)

    # Relationships
    author = db.relationship("Admins", back_populates="articles")

    def __init__(
        self, title, slug, thumbnail, content, author_id, tags, description=None
    ):
        self.title = title
        self.slug = slug
        self.thumbnail = thumbnail
        self.content = content
        self.description = description
        self.author_id = author_id
        self.status = "public"
        self.view_count = 0
        self.tags = tags
