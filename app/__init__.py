from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import sqlalchemy.orm as so


class Base(so.DeclarativeBase, so.MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix="/users")
    return app


from app import models
