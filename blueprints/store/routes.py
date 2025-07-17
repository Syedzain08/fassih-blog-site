# --- Standard Library Imports --- #
from smtplib import SMTP
from json import loads, dumps, load
from os import path, getenv

# --- Flask Core Imports --- #
from flask import (
    render_template,
    Blueprint,
    flash,
    redirect,
    request,
    abort,
    url_for,
    current_app,
    session,
    jsonify,
)

# --- Flask Extensions --- #

from flask_wtf import FlaskForm

# --- Local Application Imports --- #

from db_models import Products, db, OrderItems, Orders, ProductCategories
from forms import CheckoutForm
from email_templates import (
    create_order_confirmation_email,
    create_admin_order_alert_email,
)
from utils import dicts_equal


# --- Store Blueprint --- #


store_bp = Blueprint(
    "store", __name__, template_folder="templates", url_prefix="/store"
)


# --- Routes --- #
@store_bp.route("/")
def store_page():
    sort = request.args.get("sort", "newest")
    stock = request.args.get("stock", "all")
    category_id = request.args.get("category", "all")
    page = request.args.get("page", 1, type=int)

    query = Products.query

    if stock == "in_stock":
        query = query.filter_by(in_stock=True)
    elif stock == "out_of_stock":
        query = query.filter_by(in_stock=False)

    if category_id != "all":
        query = query.filter_by(category_id=int(category_id))

    if sort == "newest":
        query = query.order_by(Products.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(Products.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(Products.name.asc())
    elif sort == "name_desc":
        query = query.order_by(Products.name.desc())
    elif sort == "price_low":
        query = query.order_by(Products.sale_price.asc())
    elif sort == "price_high":
        query = query.order_by(Products.sale_price.desc())
    elif sort == "quantity_low":
        query = query.order_by(Products.quantity.asc())
    elif sort == "quantity_high":
        query = query.order_by(Products.quantity.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    categories = ProductCategories.query.all()

    return render_template(
        "store/store_page.html",
        products=pagination.items,
        pagination=pagination,
        sort=sort,
        stock=stock,
        categories=categories,
        selected_category=category_id,
    )


@store_bp.route("/view/product/<string:slug>")
def view_product(slug):
    product = Products.query.filter_by(slug=slug).first_or_404()
    return render_template("store/view_product.html", product=product)


@store_bp.route("/checkout/buy-now", methods=["POST", "GET"])
def buy_now():
    form = CheckoutForm()
    slug = request.form.get("slug")
    quantity = int(request.form.get("quantity", 1))
    variant_data = loads(request.form.get("variants", "{}"))

    product = Products.query.filter_by(slug=slug).first_or_404()

    if quantity < 1:
        abort(400, "Invalid quantity")

    if quantity > product.quantity:
        abort(400, "Quantity exceeds available stock")

    valid_variants = {
        (v.variant_name, v.variant_value): v.price for v in product.variants
    }
    variant_total = 0
    for name, value in variant_data.items():
        if (name, value) not in valid_variants:
            abort(400, f"Invalid variant: {name} - {value}")
        variant_total += float(valid_variants[(name, value)])

    total_price = float(product.sale_price) + variant_total
    total_price *= quantity

    product_data = {
        "slug": slug,
        "quantity": quantity,
        "variants": variant_data,
        "total_price": total_price,
    }

    return render_template(
        "store/checkout.html",
        form=form,
        product=product,
        quantity=quantity,
        selected_variants=variant_data,
        total_price=total_price,
        product_data_json=dumps(product_data),
        source="buy-now",
    )


@store_bp.route("/cart")
def cart():
    form = FlaskForm()
    cart_items = []
    total = 0

    if "cart" not in session or not session["cart"]:
        return render_template("store/cart.html", cart_items=[], total=0)

    for item in session["cart"]:
        product = Products.query.filter_by(slug=item["slug"]).first()
        if not product:
            continue

        variant_total = 0
        for name, value in item["variants"].items():
            variant = next(
                (
                    v
                    for v in product.variants
                    if v.variant_name == name and v.variant_value == value
                ),
                None,
            )
            if variant:
                variant_total += float(variant.price)

        unit_price = float(product.sale_price) + variant_total
        item_total = unit_price * item["quantity"]

        cart_items.append(
            {
                "product": product,
                "quantity": item["quantity"],
                "variants": item["variants"],
                "unit_price": unit_price,
                "total_price": item_total,
            }
        )

        total += item_total

    return render_template(
        "store/cart.html", cart_items=cart_items, total=total, form=form
    )


@store_bp.route("/checkout/add-to-cart", methods=["POST"])
def add_to_cart():
    slug = request.form.get("slug")
    quantity = int(request.form.get("quantity", 1))
    variant_data = loads(request.form.get("variants", "{}"))

    if quantity < 1:
        abort(400, "Invalid quantity")

    product = Products.query.filter_by(slug=slug).first_or_404()

    if product.quantity < quantity:
        abort(400, "Quantity exceeds available stock")

    valid_variants = {
        (v.variant_name, v.variant_value): v.price for v in product.variants
    }
    for name, value in variant_data.items():
        if (name, value) not in valid_variants:
            abort(400, f"Invalid variant: {name} - {value}")

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    for item in cart:
        if item["slug"] == slug and item["variants"] == variant_data:
            item["quantity"] += quantity
            break
    else:
        cart.append(
            {
                "slug": slug,
                "quantity": quantity,
                "variants": variant_data,
            }
        )

    session["cart"] = cart
    flash("Item added to cart.", "success")
    return redirect(url_for("store.view_product", slug=slug))


@store_bp.route("/checkout", methods=["POST"])
def process_checkout():
    form = CheckoutForm()

    # --- Load area data from areas.json ---
    areas_path = path.join(current_app.root_path, "static", "areas.json")
    with open(areas_path, "r", encoding="utf-8") as f:
        lahore_areas = load(f).get("areas", {})

    form.area.choices = [("", "Select Area")] + [
        (key, area["name"]) for key, area in lahore_areas.items()
    ]

    selected_area_key = request.form.get("area")
    if selected_area_key in lahore_areas:
        form.sub_area.choices = [("", "Select Sub Area")] + [
            (sub, sub) for sub in lahore_areas[selected_area_key]["sub_areas"]
        ]
    else:
        form.sub_area.choices = [("", "Select Sub Area")]

    if not form.validate_on_submit():

        flash("Please correct the errors in the form.", "danger")
        return redirect(url_for("index"))

    source = request.form.get("source", "cart")
    order_items = []

    if source == "buy-now":
        try:
            product_data = loads(form.product_data.data or "{}")
        except Exception:
            abort(400, "Malformed product data")

        slug = product_data.get("slug")
        quantity = int(product_data.get("quantity", 1))
        selected_variants = product_data.get("variants", {})

        if quantity < 1:
            abort(400, "Invalid quantity")

        product = Products.query.filter_by(slug=slug).first_or_404()

        if quantity > product.quantity:
            abort(400, "Quantity exceeds available stock")

        valid_variants = {
            (v.variant_name, v.variant_value): v.price for v in product.variants
        }
        variant_total = 0
        for name, value in selected_variants.items():
            if (name, value) not in valid_variants:
                abort(400, f"Invalid variant: {name} - {value}")
            variant_total += float(valid_variants[(name, value)])

        unit_price = float(product.sale_price) + variant_total
        total_price = unit_price * quantity

        order_items.append(
            OrderItems(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                variant_data=dumps(selected_variants),
            )
        )

    elif source == "cart":
        cart_items = session.get("cart", [])
        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("store.cart"))

        for item in cart_items:
            product = Products.query.filter_by(slug=item["slug"]).first()
            if not product:
                flash(f"{item['slug']} is no longer available.", "danger")
                return redirect(url_for("store.cart"))

            variant_total = 0
            for name, value in item["variants"].items():
                variant = next(
                    (
                        v
                        for v in product.variants
                        if v.variant_name == name and v.variant_value == value
                    ),
                    None,
                )
                if not variant:
                    flash(f"Invalid variant for {product.name}.", "danger")
                    return redirect(url_for("store.cart"))
                variant_total += float(variant.price)

            unit_price = float(product.sale_price) + variant_total
            total_price = unit_price * item["quantity"]

            order_items.append(
                OrderItems(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item["quantity"],
                    unit_price=unit_price,
                    total_price=total_price,
                    variant_data=dumps(item["variants"]),
                )
            )
    else:
        abort(400, "Invalid checkout source")

    total_amount = sum(item.total_price for item in order_items)

    # --- Save order ---
    order = Orders(
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        phone=form.phone.data,
        email=form.email.data,
        street_address=form.street_address.data,
        area=form.area.data,
        sub_area=form.sub_area.data,
        additional_notes=form.additional_notes.data,
        payment_method=form.payment_method.data,
        source=source,
        total_amount=total_amount,
        items=order_items,
        status="pending",
    )

    for item in order_items:
        product = Products.query.get(item.product_id)

        if not product or product.quantity is None:
            flash(f"{item.product_name} is unavailable.", "danger")
            return redirect(url_for("index"))

        if product.quantity < item.quantity:
            flash(
                f"Not enough stock for {product.name}. Only {product.quantity} left.",
                "danger",
            )
            return redirect(url_for("index"))

        product.quantity -= item.quantity
        if product.quantity == 0:
            product.in_stock = False
    try:
        db.session.add(order)
        db.session.commit()
        if source == "cart":
            session.pop("cart", None)

        server = SMTP("smtp.gmail.com", 587)
        server.starttls()
        password = getenv("GMAIL_APP_PASSWORD")
        user_address = getenv("GMAIL_ADDRESS")
        super_admin_email = getenv("SUPERADMIN_EMAIL")
        server.login(user_address, password)
        admin_msg = create_admin_order_alert_email(
            order=order, admin_email=super_admin_email
        )
        server.sendmail(
            from_addr=user_address, to_addrs=super_admin_email, msg=admin_msg.as_bytes()
        )
        msg = create_order_confirmation_email(
            order=order, recipient_email=form.email.data
        )
        server.sendmail(user_address, form.email.data, msg.as_bytes())
        server.quit()

        return redirect(url_for("store.thank_you", order_id=order.id))
    except Exception:
        db.session.rollback()
        flash(f"A Fatal Error Occured While placing your order", "danger")
        return redirect(url_for("index"))


@store_bp.route("/checkout/cart", methods=["GET", "POST"])
def cart_checkout():
    form = CheckoutForm()

    if "cart" not in session or not session["cart"]:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("store.cart"))

    cart_items = []
    total_price = 0

    for item in session["cart"]:
        product = Products.query.filter_by(slug=item["slug"]).first()
        if not product:
            flash(f"Product {item['slug']} is no longer available.", "danger")
            return redirect(url_for("store.cart"))

        if item["quantity"] > product.quantity:
            flash(
                f"Not enough stock for {product.name}. Only {product.quantity} left.",
                "danger",
            )
            return redirect(url_for("store.cart"))

        valid_variants = {
            (v.variant_name, v.variant_value): v.price for v in product.variants
        }
        variant_total = 0
        for name, value in item["variants"].items():
            if (name, value) not in valid_variants:
                flash(f"Invalid variant for {product.name}: {name} - {value}", "danger")
                return redirect(url_for("store.cart"))
            variant_total += float(valid_variants[(name, value)])

        unit_price = float(product.sale_price) + variant_total
        item_total = unit_price * item["quantity"]

        cart_items.append(
            {
                "product": product,
                "quantity": item["quantity"],
                "variants": item["variants"],
                "unit_price": unit_price,
                "total_price": item_total,
            }
        )

        total_price += item_total

    cart_data = {
        "items": session["cart"],
        "total_price": total_price,
    }

    return render_template(
        "store/checkout.html",
        form=form,
        cart_items=cart_items,
        total_price=total_price,
        cart_data_json=dumps(cart_data),
        source="cart",
    )


@store_bp.route("/clear-cart", methods=["POST"])
def clear_cart():
    try:

        session["cart"] = []
        session.modified = True

        return jsonify(
            {
                "success": True,
                "cart_total": 0,
                "cart_count": 0,
                "message": "Cart cleared",
            }
        )

    except Exception:

        return jsonify({"success": False, "message": "An error occurred"}), 500


@store_bp.route("/remove-from-cart", methods=["POST"])
def remove_from_cart():

    try:
        slug = request.form.get("slug")
        variant_data = loads(request.form.get("variants", "{}"))

        if not slug:
            return jsonify({"success": False, "message": "Invalid request"}), 400

        if "cart" not in session:
            session["cart"] = []

        cart = session["cart"]
        original_length = len(cart)

        new_cart = []
        item_removed = False

        for item in cart:
            if item["slug"] == slug and dicts_equal(item["variants"], variant_data):
                item_removed = True

                continue
            new_cart.append(item)

        session["cart"] = new_cart
        session.modified = True

        if not item_removed:
            return jsonify({"success": False, "message": "Item not found in cart"}), 404

        cart_total = 0
        for item in new_cart:
            product = Products.query.filter_by(slug=item["slug"]).first()
            if not product:
                continue

            variant_total = 0
            for name, value in item["variants"].items():
                variant = next(
                    (
                        v
                        for v in product.variants
                        if v.variant_name == name and v.variant_value == value
                    ),
                    None,
                )
                if variant:
                    variant_total += float(variant.price)

            unit_price = float(product.sale_price) + variant_total
            cart_total += unit_price * item["quantity"]

        return jsonify(
            {
                "success": True,
                "cart_total": cart_total,
                "cart_count": len(new_cart),
                "message": "Item removed from cart",
            }
        )

    except Exception:

        return jsonify({"success": False, "message": "An error occurred"}), 500


@store_bp.route("/thank-you/<uuid:order_id>")
def thank_you(order_id):
    order = Orders.query.get_or_404(order_id)
    return render_template("store/thank_you.html", order=order)
