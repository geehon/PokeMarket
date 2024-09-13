from app import db
from app.user import bp
from app.models import User as UserModel
from app.user.forms import UpdateForm
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
        user=existingUser,
        form=form
    )

@bp.route("/cart")
@login_required
def cart():

    return "WIP"
