from app.user import bp
from flask_login import login_required


@bp.route("/update/<userId>", methods=["GET", "POST"])
@login_required
def update(userId):
    return "WIP"
