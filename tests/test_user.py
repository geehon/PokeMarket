from app import db
from app.models import User as UserModel, Cart as CartModel


def test_update_get(app):
    with app.app_context():
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == "test1@mail.co".lower())
        )
    with app.test_client(user=existingUser) as client:
        res = client.get(f"/users/update/{existingUser._id}")
    assert res.request.path == f"/users/update/{existingUser._id}"
    assert res.status_code == 200
    assert b"Update User Form" in res.data


def test_home_get(app):
    with app.test_client() as client:
        res = client.get("/")
    assert res.status_code == 200


def test_cart_post(app):
    with app.app_context():
        existingUser = db.session.scalar(
            db.select(UserModel)
            .where(UserModel.email == "test1@mail.co".lower())
        )
    with app.test_client(user=existingUser) as client:
        res = client.post("users/cart", data={
            "cart_id": 0,
            "name": "cart1"
        })
        assert res.status_code == 200
        existingCart = db.session.scalar(
            db.select(CartModel)
            .where(CartModel.user_id == existingUser._id)
            .where(CartModel.name == "cart1")
        )
    assert existingCart.name == "cart1"
    with app.test_client(user=existingUser) as client:
        res = client.post("users/cart", data={
            "cart_id": 1,
            "name": "name1"
        })
        assert res.status_code == 200
        existingCart = db.session.scalar(
            db.select(CartModel)
            .where(CartModel.user_id == existingUser._id)
            .where(CartModel.name == "name1")
        )
    assert existingCart.name == "name1"
