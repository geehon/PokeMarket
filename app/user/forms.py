from app import db
from app.models import User as UserModel, Cart as CartModel
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Length
from flask_login import current_user


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
    cart_id = IntegerField("Id of cart")
    name = StringField("Cart name", validators=[DataRequired(), Length(min=2, max=29)])
    submit = SubmitField("Add")

    def validate_name(self, field):
        existingCart = db.session.scalar(
            db.select(CartModel)
            .where(CartModel.user_id == current_user.id)
            .where(CartModel.name == field.data.lower().strip())
        )
        if existingCart:
            raise ValidationError("Cart name already inuse")
