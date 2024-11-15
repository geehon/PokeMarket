from app import db
from app.auth import bp
from app.auth.forms import LoginForm, SignupForm, ForgetPasswordForm, UpdatePasswordForm
from app.models import User as UserModel, Cart as CartModel
from app.auth.utils import send_email
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlsplit


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        existingUser = db.one_or_404(
            db.select(UserModel)
            .where(UserModel.email == form.email.data)
        )
        flash(f"User login for {existingUser.username}, is Loggedin.", "success")
        login_user(existingUser, remember=form.remember.data)
        nextPage = request.args.get('next')
        if not nextPage or urlsplit(nextPage).netloc != '':
            nextPage = url_for('main.home')
        return redirect(nextPage)
    return render_template("login.html", title="Login Page", form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = SignupForm()
    if form.validate_on_submit():
        newUser = UserModel(
            username=form.name.data,
            email=form.email.data.lower(),
        )
        newUser.set_password(form.password.data)
        db.session.add(newUser)
        db.session.commit()
        #  Added default carts while creating user.
        c1 = CartModel(name="ordered", user_id=newUser.id, user=newUser)
        c2 = CartModel(name="saved for later", user_id=newUser.id, user=newUser)
        c3 = CartModel(name="cart1", user_id=newUser.id, user=newUser)
        c4 = CartModel(name="out of stock", user_id=newUser.id, user=newUser)
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()
        flash("User registered, Please login", "success")
        return redirect(url_for("auth.login"))
    return render_template("signup.html", title="Register Page", form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == form.email.data.lower())
        )
        token = existingUser.get_reset_password_token()
        subject = "Reset password for PokeMarket account"
        recipients = [existingUser.email]
        text_body = f"Go to below link\n { url_for('auth.update_password', token=token, _external=True)}"  # noqa: E501
        html_body = render_template(
            "emails/forgot_password.html",
            user=existingUser,
            token=token
        )
        send_email(subject, recipients, text_body, html_body)
        flash(f"Email has been send to {form.email.data}", "success")
        #  Return htmx template with a message box
    return render_template(
        "forgot_password.html",
        title="Forgot Password Page",
        form=form
    )


@bp.route("/update-password/<token>", methods=["GET", "POST"])
def update_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    existingUser = UserModel.verify_reset_password_token(token)
    if not existingUser:
        return redirect(url_for("main.home"))
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        existingUser.set_password(form.password.data)
        db.session.commit()
        flash("Password Updated, please login with new password", "success")
        return redirect(url_for("auth.login"))
    return render_template(
        "update_password.html",
        title="Update Password Page",
        form=form
    )
