from app import db
from app.models import User as UserModel


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
    assert b"WIP" in res.data
