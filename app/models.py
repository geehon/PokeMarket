from app import db, Base
from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import sqlalchemy.orm as so
import sqlalchemy as sa
import jwt
from time import time
from hashlib import sha256
from typing import Set, List


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


pokemonType = sa.Table(
    'pokemon_type',
    Base.metadata,
    sa.Column('pokemon_id', sa.Integer, sa.ForeignKey('pokemon._id'), primary_key=True),
    sa.Column('category_id', sa.Integer, sa.ForeignKey('category._id'), primary_key=True)  # noqa: E501
)


class Category(db.Model):
    _id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(20), index=True, unique=True)
    pokemons: so.Mapped[List['Pokemon']] = so.relationship(
        secondary=pokemonType,
        # primaryjoin=(pokemonType.c.category_id == _id),
        # secondaryjoin=lambda: pokemonType.c.pokemon_id == Pokemon._id,
        back_populates='categories', init=False)

    @staticmethod
    def all_categories():
        return [(c._id, c.name) for c in db.session.scalars(db.select(Category))]



class Pokemon(db.Model):
    _id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(60))
    desc: so.Mapped[str] = so.mapped_column(sa.Text())
    imgUrl: so.Mapped[str] = so.mapped_column(sa.String(60))
    price: so.Mapped[float] = so.mapped_column(sa.Float(2))
    quantity: so.Mapped[int] = so.mapped_column(sa.SmallInteger(), default=10)
    inStock: so.Mapped[bool] = so.mapped_column(sa.Boolean(), default=False)
    categories: so.Mapped[List['Category']] = so.relationship(
        secondary=pokemonType,
        # primaryjoin=(pokemonType.c.pokemon_id == _id),
        # secondaryjoin=lambda: pokemonType.c.category_id == Category._id,
        back_populates='pokemons', init=False)
