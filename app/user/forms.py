from app import db
from app.models import User as UserModel
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError


class UpdateForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Update")

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, field):
        if field.data.lower() == self.original_email:
            return
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == field.data.lower())
        )
        if existingUser:
            raise ValidationError("Email already taken")


class CartForm(FlaskForm):
    _id = IntegerField("Id of cart")
    name = StringField("Cart name", min=1, max=29)
