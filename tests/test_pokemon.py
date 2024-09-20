from app import db
from app.models import (
    User as UserModel,
    Pokemon as PokemonModel,
    Category as CategoryModel,
    Cart as CartModel
)


def test_category_creation(app):
    c = CategoryModel(name="test")
    with app.app_context():
        db.session.add(c)
        db.session.commit()
    with app.app_context():
        existingCategory = db.session.scalar(
            db.select(CategoryModel)
            .where(CategoryModel.name == "test")
        )

        assert existingCategory._id == 1
        assert existingCategory.name == "test"


def test_pokemon_creation(app):
    with app.app_context():
        existingCategory = db.get_or_404(CategoryModel, 1)
    p = PokemonModel(
        name="pokemon test",
        desc="This is a pokemon created in database for testing",
        inStock=True,
    )
    p.categories.append(existingCategory)
    with app.app_context():
        db.session.add(p)
        db.session.commit()
    with app.app_context():
        existingPokemon = db.session.scalar(
            db.select(PokemonModel)
            .where(PokemonModel.name == "pokemon test")
        )
        assert existingPokemon._id == 1
        assert existingPokemon.name == "pokemon test"


def test_add_pokemon_to_cart(app):
    with app.app_context():
        existingPokemon = db.get_or_404(PokemonModel, 1)
        existingUser = db.get_or_404(UserModel, 1)
        existingCart = db.session.scalar(
            db.select(CartModel)
            .where(CartModel.user_id == existingUser._id)
            .where(CartModel.name == "saved for later")
        )
        existingCart.pokemons.append(existingPokemon)
        db.session.commit()
    with app.app_context():
        existingUser = db.get_or_404(UserModel, 1)
        existingPokemon = db.get_or_404(PokemonModel, 1)
        existingCart = db.session.scalar(
            db.select(CartModel)
            .where(CartModel.user_id == existingUser._id)
            .where(CartModel.name == "saved for later")
        )
        assert existingPokemon in existingCart.pokemons


def test_pokemon_quantity(app):
    with app.app_context():
        existingPokemon = db.get_or_404(PokemonModel, 1)
        existingPokemon.quantity = 0
        db.session.commit()
    with app.app_context():
        existingPokemon = db.session.scalar(
            db.select(PokemonModel)
            .where(PokemonModel.name == "pokemon test")
        )
    assert not existingPokemon.inStock
    assert existingPokemon.quantity == 0


def test_pokemon_out_of_stock(app):
    with app.app_context():
        existingPokemon = db.get_or_404(PokemonModel, 1)
        existingUser = db.get_or_404(UserModel, 1)
        existingCart = db.session.scalar(
            db.select(CartModel)
            .where(CartModel.user_id == existingUser._id)
            .where(CartModel.name == "out of stock")
        )
        assert existingPokemon in existingCart.pokemons
