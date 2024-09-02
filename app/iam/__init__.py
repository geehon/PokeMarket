from app import admin
from app import db
from app.iam.views import UserView, PokemonView, CategoryView
from app.models import (
    User as UserModel,
    Pokemon as PokemonModel,
    Category as CategoryModel
)


admin.add_view(UserView(model=UserModel, session=db.session, endpoint="iam-user"))
admin.add_view(
    PokemonView(
        model=PokemonModel,
        session=db.session,
        endpoint="iam-pokemon"
    )
)
admin.add_view(
    CategoryView(
        model=CategoryModel,
        session=db.session,
        endpoint="iam-category"
    )
)
