from app import db
from app.auth import bp
from app.auth.forms import LoginForm, SignupForm
from app.models import User as UserModel
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from urllib.parse import urlsplit


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        existingUser = db.one_or_404(
            db.select(UserModel)
            .where(UserModel.email == form.email.data)
        )
        flash(f"User login for {existingUser.username}, is work in progress")
        login_user(existingUser, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            nextPage = url_for('main.home')
        return redirect(nextPage)
    return render_template("login.html", title="Login Page", form=form)


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        newUser = UserModel(
            username=form.name.data,
            email=form.email.data.lower(),
        )
        newUser.set_password(form.password.data)
        db.session.add(newUser)
        db.session.commit()
        flash("User registered, Please login", "success")
        return redirect(url_for("auth.login"))
    return render_template("signup.html", title="Register Page", form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))
