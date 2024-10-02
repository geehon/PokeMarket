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
from typing import List


@login_manager.user_loader
def load_user(userId):
    return db.session.get(User, userId)


class User(db.Model, UserMixin):
    _id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    username: so.Mapped[str] = so.mapped_column(sa.String(50))
    email: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256),
                                                init=False, deferred=True)

    carts: so.Mapped[List['Cart']] = so.relationship(back_populates='user', init=False)

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

    def has_pokemon(self, pokemon_id):
        cart = db.session.scalar(
            db.select(Cart)
            .where(Cart.user_id == self._id)
            .where(Cart.name != "out of stock")
            .where(Cart.name != "ordered")
            .join(pokemonCart)
            .where(pokemonCart.c.pokemon_id == pokemon_id)
        )
        return bool(cart)

    @property
    def is_admin(self):
        return self.email in current_app.config.get("ADMINS", [])


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
        primaryjoin=(pokemonType.c.category_id == _id),
        secondaryjoin=lambda: pokemonType.c.pokemon_id == Pokemon._id,
        back_populates='categories', init=False)

    @staticmethod
    def all_categories():
        return [(c._id, c.name) for c in db.session.scalars(db.select(Category))]

    def __repr__(self):
        return f"<Category({self._id}|{self.name})"


pokemonCart = sa.Table(
    "pokemons_carts",
    Base.metadata,
    sa.Column('pokemon_id', sa.Integer, sa.ForeignKey('pokemon._id'), primary_key=True, nullable=False),  # noqa: E501
    sa.Column('cart_id', sa.Integer, sa.ForeignKey('cart._id'), primary_key=True, nullable=False),  # noqa: E501
    sa.Column('quantity', sa.Integer, default=1)
)


class Pokemon(db.Model):
    _id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(60))
    desc: so.Mapped[str] = so.mapped_column(sa.Text())
    generation: so.Mapped[int] = so.mapped_column(sa.Integer, default=1)
    imgUrl: so.Mapped[str] = so.mapped_column(
        sa.String(60),
        default="https://placehold.co/400"
    )
    price: so.Mapped[float] = so.mapped_column(sa.Float(2), default=10.00)
    quantity: so.Mapped[int] = so.mapped_column(sa.SmallInteger(), default=10)
    inStock: so.Mapped[bool] = so.mapped_column(sa.Boolean(), default=False)
    categories: so.Mapped[List['Category']] = so.relationship(
        secondary=pokemonType,
        primaryjoin=(pokemonType.c.pokemon_id == _id),
        secondaryjoin=lambda: pokemonType.c.category_id == Category._id,
        back_populates='pokemons', init=False)
    carts: so.Mapped[List['Cart']] = so.relationship(
        secondary=pokemonCart, back_populates="pokemons", init=False)

    def __repr__(self):
        return (f"<Pokemon({self._id}|name: {self.name}|desc: {self.desc[:20]}|\
gen: {self.generation}|price: {self.price}|quantity: {self.quantity}|\
in stock: {self.inStock}")


@sa.event.listens_for(Pokemon.quantity, 'set')
def pokemon_got_updated(target, value, _oldValue, _initiator):
    if value < 1:
        target.inStock = False


@sa.event.listens_for(Pokemon.inStock, "set")
def remove_pokemon(target, value, _oldValue, _initiator):
    if value:
        return
    q = (db.select(User, Cart)
         .join(Cart, Cart.user_id == User._id)
         .join(pokemonCart, pokemonCart.c.cart_id == Cart._id)
         .where(pokemonCart.c.pokemon_id == target._id)
         .where(sa.or_(Cart.name != "ordered", Cart.name != "out of stock"))
         #  .distinct()
         #  .group_by(User._id)
         )
    results = db.session.execute(q).all()
    users = list()
    for user, cart in results:
        if user not in users:
            users.append(user)
        cart.pokemons.remove(target)

    for user in users:
        q = (db.select(Cart)
             .where(Cart.user_id == user._id)
             .where(Cart.name == "out of stock")
             )
        cart = db.session.scalar(q)
        cart.pokemons.append(target)


class Cart(db.Model):
    _id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(20))
    user_id: so.Mapped['int'] = so.mapped_column(sa.ForeignKey("user._id"))
    user: so.Mapped['User'] = so.relationship(back_populates='carts')
    pokemons: so.Mapped[List['Pokemon']] = so.relationship(
        secondary=pokemonCart, back_populates="carts", init=False)

    def __repr__(self):
        return f"<Cart(_id: {self._id}|name: {self.name}|user id: {self.user_id})"
