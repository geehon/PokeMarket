from app import db
from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import sqlalchemy.orm as so
import sqlalchemy as sa
import jwt
from time import time
from hashlib import sha256


@login_manager.user_loader
def load_user(userId):
    return db.session.get(User, userId)


class User(db.Model, UserMixin):
    _id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    username: so.Mapped[str] = so.mapped_column(sa.String(50))
    email: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256),
                                                init=False, deferred=True)

    def __repr__(self):
        return f"User<{self._id}|{self.username}|{self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        try:
            return str(self._id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`")

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self._id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"], algorithm="HS256"
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            _id = jwt.decode(token, current_app.config["SECRET_KEY"],
                             algorithms="HS256")["reset_password"]
        except Exception as e:
            print(e)
            return
        return db.session.get(User, _id)

    def get_profile_photo(self, size=240):
        hashed = sha256(self.email.encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{hashed}?s={size}&d=robohash"
