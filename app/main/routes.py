from app.main import bp


@bp.route("/")
@bp.route("/index")
def home():
    return "WIP"
