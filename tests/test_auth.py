from app import db
from app.models import User as UserModel


def test_signup_get(app):
    with app.test_client() as client:
        res = client.get("/auth/signup")
    assert b"<h2>Register Form</h2>" in res.data


def test_signup_post(app):
    with app.test_client() as client:
        res = client.post("/auth/signup", data={
            "name": "test1",
            "email": "test1@mail.co",
            "password": "password",
            "confirm": "password"
        },
        )
    assert res.status_code == 302
    assert res.request.path == "/auth/signup"
    with app.app_context():
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == "test1@mail.co".lower())
        )
    assert existingUser is not None


def test_login_get(app):
    with app.test_client() as client:
        res = client.get("/auth/login")
    assert b"<h2>Login Form</h2>" in res.data


def test_login_post(app):
    with app.test_client() as client:
        res = client.post("/auth/login", data={
            "email": "test1@mail.co",
            "password": "password",
        },
        )
    assert res.status_code == 302
    assert res.request.path == "/auth/login"


def test_logout(app):
    with app.app_context():
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == "test1@mail.co".lower())
        )
    with app.test_client(user=existingUser) as client:
        res = client.get("auth/logout", follow_redirects=True)
    assert res.status_code == 200
    assert res.request.path == "/index"
