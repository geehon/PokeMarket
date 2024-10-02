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
    SEND_ASYNC_MAIL = True
    RAZORPAY_CLIENT_ID = os.environ.get('RAZORPAY_CLIENT_ID') or \
        "rzp_test_JqXOtzus5lRe3E"
    RAZORPAY_CLIENT_SECRET = os.environ.get('RAZORPAY_CLIENT_SECRET') or \
        "RJVqr1g8PVnZCK0Ak9WdX7nv"
    JWT_SECRET = os.environ.get('JWT_SECRET', "its customer data")


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    WTF_CSRF_ENABLED = False
    RAZORPAY_CLIENT_ID = "rzp_test_JqXOtzus5lRe3E"
    RAZORPAY_CLIENT_SECRET = "RJVqr1g8PVnZCK0Ak9WdX7nv"
