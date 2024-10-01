from app import db
from app.main import bp
from app.models import (
    Pokemon as PokemonModel,
    pokemonCart as PokemonCartTable,
    Cart as CartModel
)
from app.auth.utils import send_email
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app
)
from flask_login import login_required, current_user
from time import time
import razorpay as rp
import os
import jwt


ID = os.environ.get("RAZORPAY_CLIENT_ID")
SECRET = os.environ.get("RAZORPAY_CLIENT_SECRET")
client = rp.Client(auth=(ID, SECRET))


@bp.route("/")
@bp.route("/index")
def home():
    query = db.select(PokemonModel)
    pokemons = db.session.scalars(query).all()
    return render_template("home.html", title="Home Page", pokemons=pokemons)


@bp.route("/return-null", methods=["DELETE"])
def return_null():
    return 'use hx-swap="delete"'


@bp.route("/terms")
def terms():
    return render_template("terms.html")


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    # ID = current_app.config.get("RAZORPAY_CLIENT_ID")
    # SECRET = current_app.config.get("RAZORPAY_CLIENT_SECRET")
    pokemons = []
    pokemon_id = request.args.get("p_id")
    cart_id = request.args.get("c_id")
    if pokemon_id:
        pokemon = db.get_or_404(PokemonModel, pokemon_id)
        pokemons.append(pokemon)
    if cart_id:
        q = (db.select(PokemonModel)
             .join(PokemonCartTable)
             .where(PokemonCartTable.c.cart_id == cart_id)
             )
        pokemons = db.session.scalars(q).all()
    client.set_app_details({
        "title": "PokeMarket",
        "version": "0.1.0"
    })
    data = get_payment_data(pokemons)
    paymentDetails = client.order.create(data=data)
    # Add all data in JWT token.
    payloadData = paymentDetails["notes"]
    payloadData["order_id"] = paymentDetails["id"]
    payloadData["exp"] = time() + 900
    token = jwt.encode(
        payloadData,
        current_app.config.get("JWT_SECRET"),
        algorithm="HS256"
    )
    session[paymentDetails['id']] = token
    return render_template(
        "checkout.html",
        title="Checkout page",
        pokemons=pokemons,
        paymentDetails=paymentDetails,
        key=ID
    )


def get_payment_data(pokemons):
    amount = 0
    data = {"currency": "INR"}
    notes = {"pokemons": []}
    for pokemon in pokemons:
        amount += int(pokemon.price) * 100
        notes["pokemons"].append(pokemon._id)
    data["amount"] = amount
    data["notes"] = notes
    return data


@bp.route("/payment-callback", methods=["POST"])
@login_required
def payment_callback():
    if not request.form.get('razorpay_signature'):
        return redirect(url_for('main.home'))
    data = {
        'razorpay_order_id': request.form.get("razorpay_order_id"),
        'razorpay_payment_id': request.form.get("razorpay_payment_id"),
        'razorpay_signature': request.form.get("razorpay_signature")
    }
    if not client.utility.verify_payment_signature(data):
        flash("Payment was not successfull, please try again.", "error")
        return redirect(url_for("main.home"))
    token = session.pop(data.get('razorpay_order_id'))
    try:
        orderData = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms="HS256"
        )
    except Exception:
        flash("Payment was not successfull, please try again.", "error")
        return redirect(url_for("main.home"))
    q = (db.select(CartModel)
         .where(CartModel.user_id == current_user._id)
         .where(CartModel.name == "ordered")
         )
    cart = db.session.scalar(q)
    pokemons = []
    for p_id in orderData["pokemons"]:
        p = db.get_or_404(PokemonModel, p_id)
        cart.pokemons.append(p)
        pokemons.append(p)
    db.session.commit()
    subject = "Pokemon bought from PokeMarket"
    recipients = [current_user.email]
    text_body = f"Thanks for buying pokemon, {request.form.get('razorpay_payment_id')} this is razor payment id"  # noqa: E501
    html_body = render_template(
        "emails/pokemon_bought.html",
        pokemons=pokemons,
        razorpay_id=request.form.get('razorpay_payment_id')
    )
    send_email(subject, recipients, text_body, html_body)
    flash(f"{current_user.username} bought pokemons", "success")
    return redirect(url_for("user.cart"))
