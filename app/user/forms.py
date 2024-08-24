from app import db
from app.models import User as UserModel
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class UpdateForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Update")

    def validate_email(self, field):
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == field.data.lower())
        )
        if existingUser:
            raise ValidationError("Email already taken")
