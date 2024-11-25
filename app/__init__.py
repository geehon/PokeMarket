from config import Config
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlalchemy.orm as so


class AdminHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated:
            if current_user.is_admin:
                return super(AdminHomeView, self).index()
        abort(404)


class Base(so.DeclarativeBase, so.MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
mail = Mail()
admin = Admin(name="PokeMarket", index_view=AdminHomeView())
limiter = Limiter(key_func=get_remote_address, default_limits=["50 per hour"])


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    admin.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/users")
    return app


from app import models
from app import iam
