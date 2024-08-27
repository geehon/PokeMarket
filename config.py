import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "you'll never know"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        "sqlite:///debug.db"
    ADMINS = ['gpt.sahaj28@gmail.com']
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = "gpt.sahaj28@gmail.com"


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    WTF_CSRF_ENABLED = False
    MAIL_SERVER = "localhost"
    MAIL_PORT = 8025
