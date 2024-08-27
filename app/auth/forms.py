from app import db
from app.models import User as UserModel
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    remember = BooleanField("Remember me?", default=True)
    submit = SubmitField("Login")

    def validate_email(self, field):
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == field.data.lower())
        )

        if not existingUser:
            raise ValidationError("No Account with this email")

    def validate_password(self, field):
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == self.email.data.lower())
        )

        if not existingUser.check_password(field.data):
            raise ValidationError("Incorrect password")


class SignupForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo("confirm", message="Password does not match")
        ]
    )
    confirm = PasswordField("Repeat password")
    submit = SubmitField("Register")

    def validate_email(self, field):
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == field.data.lower())
        )
        if existingUser:
            raise ValidationError("Email already taken")


class ForgetPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Send link")

    def validate_email(self, field):
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == field.data.lower())
        )
        if not existingUser:
            raise ValidationError("No Account with this email")


class UpdatePasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo("confirm", message="Password does not match")
        ]
    )
    confirm = PasswordField("Repeat password")
    submit = SubmitField("Update Password")
