from app import db
from app.user import bp
from app.models import Cart as CartModel, Pokemon as PokemonModel
from app.user.forms import UpdateForm, CartForm
from flask_login import login_required, current_user
from flask import render_template, flash


@bp.route("/update/<userId>", methods=["GET", "POST"])
@login_required
def update(userId):
    form = UpdateForm(current_user.email)
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.email = form.email.data.lower()
        db.session.commit()
        flash(f"User details for { form.name.data }, is updated.", "success")
    return render_template(
        "account.html",
        title="Update profile",
        user=current_user,
        form=form
    )


@bp.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    query = (db.select(CartModel)
             .where(CartModel.user == current_user)
             .order_by(CartModel._id.desc()))
    carts = db.session.scalars(query).all()
    form = CartForm()
    if form.validate_on_submit():
        if form.cart_id.data:
            existingCart = db.get_or_404(CartModel, form.cart_id.data)
            existingCart.name = form.name.data.lower()
            flash("Cart name updated", "success")
        else:
            newCart = CartModel(
                name=form.name.data,
                user_id=current_user._id,
                user=current_user
            )
            db.session.add(newCart)
            flash("Cart added", "success")
        db.session.commit()
    return render_template(
        "cart.html",
        title="Carts page",
        carts=carts,
        form=form
    )


@bp.route("/cart/<pokemon_id>/add", methods=["PUT"])
@login_required
def add_to_cart(pokemon_id):
    query = (db.select(CartModel)
             .where(CartModel.user == current_user)
             .order_by(CartModel._id.desc()))
    cart = db.session.scalar(query)
    pokemon = db.get_or_404(PokemonModel, pokemon_id)
    cart.pokemons.append(pokemon)
    db.session.commit()
    return f"{pokemon_id} will be added to cart"
