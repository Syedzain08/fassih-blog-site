# --- Standard Library Imports --- #
from json import loads, JSONDecodeError
from smtplib import SMTP


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
from sqlalchemy import func, asc, desc, or_

# --- Local Application Imports --- #
from db_models import (
    db,
    Admins,
    Articles,
    ProductCategories,
    Products,
    ProductImages,
    ProductVariants,
    Orders,
    Bookings,
    OrderItems,
)
from forms import (
    AddAdminForm,
    DeleteAdminForm,
    AddArticleForm,
    ProductForm,
    AddCategoryForm,
    CancelOrderForm,
    CompleteOrderForm,
    CancelBookingForm,
    CompleteBookingForm,
    ConfirmBookingForm,
)
from utils import (
    check_username_criteria,
    generate_unique_slug,
    generate_throwaway_password,
    ping_google,
)


from email_templates import (
    create_order_cancellation_email,
    create_order_completion_email,
    create_booking_cancellation_email,
    create_booking_confirmation_email,
    create_booking_completion_email,
)


from os import getenv
from uuid import UUID


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
    total_articles = Articles.query.count()
    total_views = db.session.query(func.sum(Articles.view_count)).scalar() or 0
    pending_orders = Orders.query.filter_by(status="pending").count()
    total_products = Products.query.count()

    return render_template(
        "admin/dashboard.html",
        total_articles=total_articles,
        total_views=total_views,
        pending_orders=pending_orders,
        total_products=total_products,
    )


@admin_bp.route("/manage/admins", methods=["GET", "POST"])
@login_required
def manage_admins():
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


@admin_bp.route("/manage/articles", methods=["POST", "GET"])
@login_required
def manage_articles():
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort", "newest")
    status_filter = request.args.get("status", "public")
    per_page = 12
    search_query = request.args.get("q", "").strip()

    query = Articles.query

    if search_query:
        search_filter = or_(
            Articles.title.ilike(f"%{search_query}%"),
            Articles.description.ilike(f"%{search_query}%"),
            Articles.tags.ilike(f"%{search_query}%"),
            Articles.content.ilike(f"%{search_query}%"),
            Articles.slug.ilike(f"%{search_query}%"),
        )
        query = query.filter(search_filter)

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
        "admin/manage_articles.html",
        articles=articles,
        pagination=pagination,
        total_articles=total_articles,
        current_sort=sort_by,
        current_status=status_filter,
        search_query=search_query,
    )


@admin_bp.route("/add/article", methods=["GET", "POST"])
@login_required
def add_article():

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
            ping_google()
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


@admin_bp.route("/articles/<int:article_id>/delete", methods=["POST"])
@login_required
def delete_article(article_id):

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


@admin_bp.route("/manage/products")
@login_required
def manage_products():
    form = AddCategoryForm()
    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort", "newest")
    category = request.args.get("category", "all")
    status_filter = request.args.get("status", "all")
    search_query = request.args.get("q", "").strip()
    per_page = 12

    query = Products.query
    categories = ProductCategories.query.all()

    if search_query:
        search_filter = or_(
            Products.name.ilike(f"%{search_query}%"),
            Products.description.ilike(f"%{search_query}%"),
            Products.tags.ilike(f"%{search_query}%"),
            Products.animal_type.ilike(f"%{search_query}%"),
            Products.form_type.ilike(f"%{search_query}%"),
        )
        query = query.filter(search_filter)

    if category != "all":
        query = query.filter(Products.category_id == int(category))

    if status_filter == "in_stock":
        query = query.filter(Products.in_stock == True)
    elif status_filter == "out_of_stock":
        query = query.filter(Products.in_stock == False)

    if sort_by == "newest":
        query = query.order_by(desc(Products.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Products.created_at))
    elif sort_by == "name_asc":
        query = query.order_by(asc(Products.name))
    elif sort_by == "name_desc":
        query = query.order_by(desc(Products.name))
    elif sort_by == "price_low":
        query = query.order_by(asc(Products.sale_price))
    elif sort_by == "price_high":
        query = query.order_by(desc(Products.sale_price))
    elif sort_by == "quantity_low":
        query = query.order_by(asc(Products.quantity))
    elif sort_by == "quantity_high":
        query = query.order_by(desc(Products.quantity))
    else:
        query = query.order_by(desc(Products.created_at))

    total_products = query.count()
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return render_template(
        "admin/manage_products.html",
        products=products,
        pagination=pagination,
        total_products=total_products,
        current_sort=sort_by,
        current_status=status_filter,
        search_query=search_query,
        form=form,
        categories=categories,
        current_category=category,
    )


@admin_bp.route("/add/product", methods=["GET", "POST"])
@login_required
def add_product():
    form = ProductForm()
    categories = ProductCategories.query.all()

    if categories:
        form.populate_categories(categories)
    else:
        form.category_id.choices = [("", "No categories available")]

    if form.validate_on_submit():

        try:

            name = form.name.data
            description = form.description.data
            purchase_price = form.purchase_price.data
            sale_price = form.sale_price.data
            quantity = form.quantity.data
            in_stock = form.in_stock.data
            tags = form.tags.data
            category_id = form.category_id.data or None

            animal_type = form.animal_type.data
            if animal_type == "other":
                animal_type = request.form.get("custom_animal_type", "").strip()

            form_type = form.form_type.data
            if form_type == "other":
                form_type = request.form.get("custom_form_type", "").strip()

            slug = generate_unique_slug(title=name, model=Products)

            new_product = Products(
                name=name,
                slug=slug,
                description=description,
                purchase_price=purchase_price,
                sale_price=sale_price,
                quantity=quantity,
                in_stock=in_stock,
                tags=tags,
                animal_type=animal_type or None,
                form_type=form_type or None,
                category_id=category_id,
            )

            db.session.add(new_product)
            db.session.flush()

            image_urls_data = None

            single_value = request.form.get("image_urls")
            if single_value and single_value.strip():
                image_urls_data = single_value
            else:

                image_urls_list = request.form.getlist("image_urls")
                for item in reversed(image_urls_list):
                    if item and item.strip():
                        image_urls_data = item
                        break

            if image_urls_data and image_urls_data.strip():
                try:
                    images_data = loads(image_urls_data)

                    if isinstance(images_data, list):
                        for index, image_data in enumerate(images_data):
                            if isinstance(image_data, dict) and "url" in image_data:
                                new_image = ProductImages(
                                    product_id=new_product.id,
                                    image_url=image_data["url"],
                                    is_primary=image_data.get("is_primary", False),
                                    order_index=index,
                                )
                                db.session.add(new_image)

                            else:
                                flash("Invalid image data format", "danger")
                    else:
                        flash("Images data is not a list", "danger")

                except JSONDecodeError:

                    flash("Invalid image data format", "danger")
                except Exception:
                    flash("Image processing error: ", "danger")
            else:
                flash("No valid image data received", "danger")

            # Handle variants
            variant_names, variant_values, variant_prices = {}, {}, {}

            for key, value in request.form.items():
                if key.startswith("variant_name_"):
                    variant_id = key.split("_")[-1]
                    variant_names[variant_id] = value
                elif key.startswith("variant_value_"):
                    variant_id = key.split("_")[-1]
                    values = request.form.getlist(f"variant_value_{variant_id}[]")
                    variant_values[variant_id] = values

                elif key.startswith("variant_price_"):
                    variant_id = key.split("_")[-1]
                    prices = request.form.getlist(f"variant_price_{variant_id}[]")
                    variant_prices[variant_id] = prices

            variant_ids = [
                key.split("_")[-1]
                for key in request.form.keys()
                if key.startswith("variant_name_")
            ]
            for variant_id in variant_ids:
                variant_name = request.form.get(f"variant_name_{variant_id}")
                values = request.form.getlist(f"variant_value_{variant_id}[]")
                prices = request.form.getlist(f"variant_price_{variant_id}[]")

                for value, price in zip(values, prices):
                    if value and price:
                        try:
                            db.session.add(
                                ProductVariants(
                                    product_id=new_product.id,
                                    variant_name=variant_name,
                                    variant_value=value,
                                    price=float(price),
                                )
                            )
                        except ValueError:
                            flash(
                                f"Invalid price for variant {variant_name}: {value}",
                                "error",
                            )

            db.session.commit()
            ping_google()
            flash("Product created successfully!", "success")
            return redirect(url_for("admin.manage_products"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating product: {str(e)}", "error")

    return render_template("admin/add_product.html", form=form, is_edit=False)


@admin_bp.route("/edit/product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Products.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    categories = ProductCategories.query.all()

    if categories:
        form.populate_categories(categories)

    if form.validate_on_submit():
        try:
            form.populate_obj(product)

            animal_type = form.animal_type.data
            if animal_type == "other":
                animal_type = request.form.get("custom_animal_type", "").strip()
            product.animal_type = animal_type or None

            form_type = form.form_type.data
            if form_type == "other":
                form_type = request.form.get("custom_form_type", "").strip()
            product.form_type = form_type or None

            product.category_id = form.category_id.data or None

            image_urls_data = None

            single_value = request.form.get("image_urls")
            if single_value and single_value.strip():
                image_urls_data = single_value
            else:
                image_urls_list = request.form.getlist("image_urls")
                for item in reversed(image_urls_list):
                    if item and item.strip():
                        image_urls_data = item
                        break

            if image_urls_data and image_urls_data.strip():
                try:
                    images_data = loads(image_urls_data)

                    if isinstance(images_data, list):
                        ProductImages.query.filter_by(product_id=product.id).delete()

                        for index, image_data in enumerate(images_data):
                            if isinstance(image_data, dict) and "url" in image_data:
                                new_image = ProductImages(
                                    product_id=product.id,
                                    image_url=image_data["url"],
                                    is_primary=image_data.get("is_primary", False),
                                    order_index=index,
                                )
                                db.session.add(new_image)

                except JSONDecodeError:
                    flash("Invalid image data format", "danger")
                except Exception:
                    flash("Image processing error", "danger")

            ProductVariants.query.filter_by(product_id=product.id).delete()

            variant_ids = [
                key.split("_")[-1]
                for key in request.form.keys()
                if key.startswith("variant_name_")
            ]

            for variant_id in variant_ids:
                variant_name = request.form.get(f"variant_name_{variant_id}")
                values = request.form.getlist(f"variant_value_{variant_id}[]")
                prices = request.form.getlist(f"variant_price_{variant_id}[]")

                for value, price in zip(values, prices):
                    if value and price:
                        try:
                            db.session.add(
                                ProductVariants(
                                    product_id=product.id,
                                    variant_name=variant_name,
                                    variant_value=value,
                                    price=float(price),
                                )
                            )
                        except ValueError:
                            flash(
                                f"Invalid price for variant {variant_name}: {value}",
                                "error",
                            )

            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("admin.manage_products"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating product: {str(e)}", "error")

    existing_variants = ProductVariants.query.filter_by(product_id=product.id).all()

    variants_grouped = {}
    for variant in existing_variants:
        if variant.variant_name not in variants_grouped:
            variants_grouped[variant.variant_name] = []
        variants_grouped[variant.variant_name].append(
            {"value": variant.variant_value, "price": variant.price}
        )

    existing_images = (
        ProductImages.query.filter_by(product_id=product.id)
        .order_by(ProductImages.order_index)
        .all()
    )
    images_data = []
    for img in existing_images:
        images_data.append({"url": img.image_url, "is_primary": img.is_primary})

    return render_template(
        "admin/add_product.html",
        form=form,
        product=product,
        is_edit=True,
        existing_variants=variants_grouped,
        existing_images=images_data,
    )


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    product_to_delete = Products.query.filter_by(id=product_id).first()

    if not product_to_delete:
        flash("Product doesn't exist", "danger")
        return redirect(url_for("admin.manage_products"))

    try:

        orders_to_cancel = (
            db.session.query(Orders)
            .join(OrderItems)
            .filter(
                OrderItems.product_id == product_id,
                Orders.status.in_(["pending"]),
            )
            .all()
        )

        for order in orders_to_cancel:

            for item in order.items:
                if item.product_id != product_id:
                    product = Products.query.get(item.product_id)
                    if product:
                        product.quantity += item.quantity

            order.status = "cancelled"

            try:
                server = SMTP("smtp.gmail.com", 587)
                server.starttls()
                password = getenv("GMAIL_APP_PASSWORD")
                user_address = getenv("GMAIL_ADDRESS")
                server.login(user_address, password)

                reason = f"Product '{product_to_delete.name}' has been discontinued and is no longer available."
                msg = create_order_cancellation_email(
                    order, recipient_email=order.email, reason=reason
                )

                server.sendmail(
                    from_addr=user_address, to_addrs=order.email, msg=msg.as_bytes()
                )
                server.quit()

            except Exception as email_error:
                print(
                    f"Failed to send cancellation email for order {order.id}: {email_error}"
                )

        db.session.delete(product_to_delete)
        db.session.commit()

        success_msg = "Product deleted successfully"
        if orders_to_cancel:
            success_msg += f" and {len(orders_to_cancel)} orders were cancelled"

        flash(success_msg, "success")
        return redirect(url_for("admin.manage_products"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {e}", "error")
        return redirect(url_for("admin.manage_products"))


@admin_bp.route("/add/category", methods=["POST"])
@login_required
def add_category():
    form = AddCategoryForm()

    if form.validate_on_submit():
        name = form.name.data.lower().strip()

        existing = ProductCategories.query.filter_by(name=name).first()
        if existing:
            flash("Category with that name already exists.", "danger")
            return redirect(url_for("admin.manage_products"))

        slug = generate_unique_slug(name, ProductCategories)

        new_category = ProductCategories(name=name, slug=slug)

        try:
            db.session.add(new_category)
            db.session.commit()
            flash("New category added successfully.", "success")
            return redirect(url_for("admin.manage_products"))
        except Exception:
            db.session.rollback()
            flash(
                f"A fatal error occurred while trying to add a new category", "danger"
            )
            return redirect(url_for("admin.manage_products"))
    flash("Form submission failed. Please check your input.", "danger")
    return redirect(url_for("admin.manage_products"))


@admin_bp.route("/manage/orders")
def manage_orders():
    status = request.args.get("status", "pending")
    page = request.args.get("page", 1, type=int)
    per_page = 12

    pagination = (
        Orders.query.filter_by(status=status)
        .order_by(Orders.created_at.desc())
        .paginate(page=page, per_page=per_page)
    )

    return render_template(
        "admin/manage_orders.html",
        orders=pagination.items,
        pagination=pagination,
        current_status=status,
        cancel_form=CancelOrderForm(),
        complete_form=CompleteOrderForm(),
    )


@admin_bp.route("/orders/<uuid:order_id>/complete", methods=["POST"])
def complete_order(order_id):
    order = Orders.query.get_or_404(order_id)
    order.status = "completed"
    try:

        db.session.commit()
        flash("Order marked as completed.", "success")

        server = SMTP("smtp.gmail.com", 587)
        server.starttls()
        password = getenv("GMAIL_APP_PASSWORD")
        user_address = getenv("GMAIL_ADDRESS")

        server.login(user_address, password)

        msg = create_order_completion_email(order, recipient_email=order.email)

        server.sendmail(
            from_addr=user_address, to_addrs=order.email, msg=msg.as_bytes()
        )

        server.quit()
    except Exception:
        db.session.rollback()
        flash(f"something went wrong", "danger")
        return redirect(url_for("admin.manage_orders", status="pending"))

    return redirect(url_for("admin.manage_orders", status="pending"))


@admin_bp.route("/orders/<uuid:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    form = CancelOrderForm()
    if form.validate_on_submit():
        try:
            order = Orders.query.get_or_404(order_id)

            # Restore inventory
            for item in order.items:
                product = Products.query.get(item.product_id)
                if product:
                    product.quantity += item.quantity

            order.status = "cancelled"
            db.session.commit()

            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            password = getenv("GMAIL_APP_PASSWORD")
            user_address = getenv("GMAIL_ADDRESS")

            server.login(user_address, password)
            if form.reason == "":
                form.reason = None
            msg = create_order_cancellation_email(
                order, recipient_email=order.email, reason=form.reason.data.strip()
            )

            server.sendmail(
                from_addr=user_address, to_addrs=order.email, msg=msg.as_bytes()
            )

            server.quit()
            flash("Order cancelled and inventory restored.", "warning")

        except Exception as e:
            db.session.rollback()

            flash(f"An error occurred while cancelling the order. {e}", "danger")

    return redirect(url_for("admin.manage_orders", status="pending"))


@admin_bp.route("/manage/bookings")
def manage_bookings():
    status = request.args.get("status", "pending")
    page = request.args.get("page", 1, type=int)
    per_page = 12

    pagination = (
        Bookings.query.filter_by(status=status)
        .order_by(Bookings.created_at.desc())
        .paginate(page=page, per_page=per_page)
    )

    return render_template(
        "admin/manage_bookings.html",
        bookings=pagination.items,
        pagination=pagination,
        current_status=status,
        cancel_form=CancelBookingForm(),
        confirm_form=ConfirmBookingForm(),
        complete_form=CompleteBookingForm(),
    )


@admin_bp.route("/bookings/<booking_id>/confirm", methods=["POST"])
def confirm_booking(booking_id):
    form = ConfirmBookingForm()
    valid_booking_id = UUID(booking_id)

    if form.validate_on_submit():
        try:
            booking = Bookings.query.get_or_404(valid_booking_id)
            booking.status = "confirmed"
            db.session.commit()

            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            password = getenv("GMAIL_APP_PASSWORD")
            user_address = getenv("GMAIL_ADDRESS")

            server.login(user_address, password)

            msg = create_booking_confirmation_email(
                booking=booking, recipient_email=booking.email
            )

            server.sendmail(
                from_addr=user_address, to_addrs=booking.email, msg=msg.as_bytes()
            )

            server.quit()

            flash(f"Booking #{booking.id} has been confirmed successfully.", "success")
        except Exception:
            db.session.rollback()
            flash("An error occurred while confirming the booking.", "danger")

    return redirect(url_for("admin.manage_bookings"))


@admin_bp.route("/bookings/<booking_id>/complete", methods=["POST"])
def complete_booking(booking_id):
    form = CompleteBookingForm()
    valid_booking_id = UUID(booking_id)

    if form.validate_on_submit():
        try:
            booking = Bookings.query.get_or_404(valid_booking_id)
            booking.status = "completed"
            db.session.commit()

            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            password = getenv("GMAIL_APP_PASSWORD")
            user_address = getenv("GMAIL_ADDRESS")

            server.login(user_address, password)

            msg = create_booking_completion_email(
                booking=booking, recipient_email=booking.email
            )

            server.sendmail(
                from_addr=user_address, to_addrs=booking.email, msg=msg.as_bytes()
            )

            server.quit()

            flash(f"Booking #{booking.id} has been marked as completed.", "success")

        except Exception as e:
            db.session.rollback()
            flash("An error occurred while completing the booking.", "danger")

    return redirect(url_for("admin.manage_bookings"))


@admin_bp.route("/bookings/<booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    form = CancelBookingForm()
    valid_booking_id = UUID(booking_id)

    if form.validate_on_submit():
        try:
            booking = Bookings.query.get_or_404(valid_booking_id)
            booking.status = "cancelled"
            db.session.commit()

            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            password = getenv("GMAIL_APP_PASSWORD")
            user_address = getenv("GMAIL_ADDRESS")

            server.login(user_address, password)

            msg = create_booking_cancellation_email(
                booking=booking,
                recipient_email=booking.email,
                reason=form.reason.data.strip(),
            )

            server.sendmail(
                from_addr=user_address, to_addrs=booking.email, msg=msg.as_bytes()
            )

            server.quit()

            flash(f"Booking #{booking.id} has been cancelled.", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while cancelling the booking.", "danger")

    return redirect(url_for("admin.manage_bookings"))
