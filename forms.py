from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    HiddenField,
    TextAreaField,
    SelectField,
    DecimalField,
    IntegerField,
    BooleanField,
    EmailField,
    TelField,
    RadioField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Optional,
    NumberRange,
    InputRequired,
)


class LoginForm(FlaskForm):
    username = StringField(
        "username", validators=[DataRequired(), Length(min=3, max=35)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ForgotUsernameOrPassword(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(min=6, max=120),
            Email(message="Invalid email format"),
        ],
    )
    submit = SubmitField("Submit")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class AddAdminForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=35)]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(min=6, max=120),
            Email(message="Invalid email format"),
        ],
    )
    submit = SubmitField("Add Admin")


class DeleteAdminForm(FlaskForm):
    admin_id = HiddenField("Admin ID", validators=[DataRequired()])
    submit = SubmitField("Delete Admin")


class AddArticleForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField(
        "Description", validators=[DataRequired(), Length(min=12)]
    )
    content = TextAreaField("Content")
    tags = StringField("Tags")
    status = SelectField(
        "Status",
        choices=[("public", "Public"), ("private", "Private")],
        default="public",
    )
    submit = SubmitField("Publish Post")


class ProductForm(FlaskForm):
    name = StringField(
        "Product Name",
        validators=[DataRequired(), Length(min=2, max=255)],
        render_kw={"placeholder": "Enter product name"},
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()],
        render_kw={"placeholder": "Enter product description"},
    )

    category_id = SelectField(
        "Category",
        validators=[Optional()],
        coerce=int,
        choices=[],
        render_kw={"placeholder": "Select category"},
    )

    animal_type = SelectField(
        "Animal Type",
        validators=[Optional()],
        choices=[
            ("", "Select Animal Type"),
            ("canine", "Canine"),
            ("feline", "Feline"),
            ("reptile", "Reptile"),
            ("goat", "Goat"),
            ("sheep", "Sheep"),
            ("buffalo", "Buffalo"),
            ("cow", "Cow"),
            ("lion", "Lion"),
            ("bird", "Bird"),
            ("cat", "Cat"),
            ("dog", "Dog"),
            ("rabbit", "Rabbit"),
            ("hamster", "Hamster"),
            ("fish", "Fish"),
            ("horse", "Horse"),
            ("pig", "Pig"),
            ("chicken", "Chicken"),
            ("duck", "Duck"),
            ("turkey", "Turkey"),
            ("other", "Other (Custom)"),
        ],
    )

    form_type = SelectField(
        "Form Type",
        validators=[Optional()],
        choices=[
            ("", "Select Form Type"),
            ("tablet", "Tablet"),
            ("capsule", "Capsule"),
            ("liquid", "Liquid"),
            ("powder", "Powder"),
            ("injection", "Injection"),
            ("spray", "Spray"),
            ("cream", "Cream"),
            ("ointment", "Ointment"),
            ("gel", "Gel"),
            ("drops", "Drops"),
            ("feed", "Feed"),
            ("supplement", "Supplement"),
            ("vaccine", "Vaccine"),
            ("other", "Other (Custom)"),
        ],
    )

    purchase_price = DecimalField(
        "Purchase Price",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
        render_kw={"placeholder": "0.00"},
    )

    sale_price = DecimalField(
        "Sale Price",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
        render_kw={"placeholder": "0.00"},
    )

    quantity = IntegerField(
        "Quantity",
        validators=[DataRequired(), NumberRange(min=0)],
        default=0,
        render_kw={"placeholder": "0"},
    )

    in_stock = BooleanField("In Stock", default=False)

    tags = StringField(
        "Tags",
        validators=[Optional()],
        render_kw={"placeholder": "Enter tags separated by commas"},
    )

    image_urls = HiddenField()

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

    def populate_categories(self, categories):

        self.category_id.choices = [(-1, "Select Category")] + [
            (cat.id, cat.name) for cat in categories
        ]


class ProductVariantForm(FlaskForm):

    variant_name = StringField(
        "Variant Name",
        validators=[DataRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "e.g., Weight, Size, Color"},
    )

    variant_value = StringField(
        "Variant Value",
        validators=[DataRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "e.g., 2kg, Large, Red"},
    )

    price = DecimalField(
        "Price",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
        render_kw={"placeholder": "0.00"},
    )


class AddCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField("Add Category")


class CheckoutForm(FlaskForm):

    product_data = HiddenField("Product Data")

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(message="First name is required"),
            Length(
                min=2, max=50, message="First name must be between 2 and 50 characters"
            ),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Last name is required"),
            Length(
                min=2, max=50, message="Last name must be between 2 and 50 characters"
            ),
        ],
    )

    phone = TelField(
        "Phone Number",
        validators=[
            DataRequired(message="Phone number is required"),
            Length(min=10, max=15, message="Please enter a valid phone number"),
        ],
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Please enter a valid email address"),
        ],
    )

    street_address = StringField(
        "Street Address",
        validators=[
            DataRequired(message="Street address is required"),
            Length(
                min=5,
                max=200,
                message="Street address must be between 5 and 200 characters",
            ),
        ],
    )

    area = SelectField(
        "Area", validators=[DataRequired(message="Please select an area")], choices=[]
    )

    sub_area = SelectField(
        "Sub Area",
        validators=[DataRequired(message="Please select a sub area")],
        choices=[],
    )

    additional_notes = TextAreaField(
        "Additional Notes",
        validators=[
            Optional(),
            Length(max=500, message="Notes cannot exceed 500 characters"),
        ],
    )

    payment_method = RadioField(
        "Payment Method",
        choices=[("cod", "Cash on Delivery (COD)")],
        default="cod",
        validators=[InputRequired()],
    )

    submit = SubmitField("Place Order")

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)

        self.area.choices = [("", "Select Area")]
        self.sub_area.choices = [("", "Select Sub Area")]


class CartUpdateForm(FlaskForm):

    action = SelectField(
        "Action",
        choices=[
            ("increase", "Increase Quantity"),
            ("decrease", "Decrease Quantity"),
            ("remove", "Remove Item"),
            ("clear", "Clear Cart"),
            ("update_quantity", "Update Quantity"),
        ],
        validators=[DataRequired()],
    )
    product_slug = StringField("Product Slug", validators=[Optional()])
    variants = HiddenField("Variants", validators=[Optional()])
    quantity = IntegerField(
        "Quantity", validators=[Optional(), NumberRange(min=1, max=999)], default=1
    )
    submit = SubmitField("Update Cart")


class CartForm(FlaskForm):

    submit = SubmitField("Proceed to Checkout")


class QuickUpdateForm(FlaskForm):

    product_slug = StringField("Product Slug", validators=[DataRequired()])
    variants = HiddenField("Variants", validators=[Optional()])
    new_quantity = IntegerField(
        "New Quantity", validators=[DataRequired(), NumberRange(min=0, max=999)]
    )
    submit = SubmitField("Update")


class CancelOrderForm(FlaskForm):
    reason = TextAreaField("Reason (optional)", validators=[Optional()])
    submit = SubmitField("Confirm Cancel")


class CompleteOrderForm(FlaskForm):
    submit = SubmitField("Mark as Completed")
