from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    HiddenField,
    TextAreaField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, Email


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
