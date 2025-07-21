from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID


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


class ProductCategories(db.Model):
    __tablename__ = "ProductCategories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships

    products = db.relationship("Products", back_populates="category")


class Products(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    in_stock = db.Column(db.Boolean, default=False, nullable=False)
    tags = db.Column(db.Text, nullable=True)
    animal_type = db.Column(db.String(50), nullable=True)
    form_type = db.Column(db.String(50), nullable=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("ProductCategories.id"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    category = db.relationship("ProductCategories", back_populates="products")
    images = db.relationship(
        "ProductImages", back_populates="product", cascade="all, delete-orphan"
    )
    variants = db.relationship(
        "ProductVariants", back_populates="product", cascade="all, delete-orphan"
    )


class ProductImages(db.Model):
    __tablename__ = "ProductImages"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("Products.id", ondelete="CASCADE"),
        nullable=False,
    )
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    product = db.relationship("Products", back_populates="images")


class ProductVariants(db.Model):
    __tablename__ = "ProductVariants"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("Products.id", ondelete="CASCADE"), nullable=False
    )
    variant_name = db.Column(db.String(100), nullable=False)
    variant_value = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    product = db.relationship("Products", back_populates="variants")


class OrderItems(db.Model):
    __tablename__ = "Order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("Orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("Products.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_name = db.Column(db.String(255), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    variant_data = db.Column(db.Text, nullable=True)


class Orders(db.Model):
    __tablename__ = "Orders"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    street_address = db.Column(db.String(255), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    sub_area = db.Column(db.String(100), nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)

    payment_method = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")

    total_amount = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItems", backref="order", cascade="all, delete-orphan")


class Bookings(db.Model):
    __tablename__ = "Bookings"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)

    service_type = db.Column(db.String(100), nullable=False)
    animal_type = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)

    status = db.Column(db.String(80), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
