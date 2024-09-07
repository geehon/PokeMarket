from app import db
from app.main import bp
from app.models import Pokemon as PokemonModel
from flask import render_template


@bp.route("/")
@bp.route("/index")
def home():
    query = db.select(PokemonModel)
    pokemons = db.session.scalars(query).all()
    return render_template("home.html", title="Home Page", pokemons=pokemons)


@bp.route("/return-null", methods=["DELETE"])
def return_null():
    return 'use hx-swap="delete"'
