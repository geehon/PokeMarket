from app import db
from app.models import (
    Pokemon as PokemonModel,
    Category as CategoryModel,
)
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import SelectMultipleField
# TODO: Read about flask_admin.contrib.sqla.fields.QuerySelectMultipleField as a replacement for SelectMultipleField # noqa: E501


class UserView(ModelView):
    column_exclude_list = ["password"]
    column_searchable_list = ["email"]
    can_create = False
    form_excluded_columns = ["password"]
    pass


class PokemonView(ModelView):
    page_size = 50
    column_list = [
        PokemonModel._id,
        PokemonModel.name,
        PokemonModel.price,
        PokemonModel.quantity,
        PokemonModel.inStock,
        "categories"
    ]
    column_filters = ["price", "categories"]
    column_formatters = dict(
        categories=lambda v, c, m, n: [c.name for c in m.categories]
    )
    # edit page of PokemonView.

    def list_choices():
        return [
            (c._id, c.name)
            for c in db.session.scalars(db.select(CategoryModel)).all()
        ]

    def coerce_obj(v):
        if isinstance(v, CategoryModel):
            return v
        category = db.session.scalar(
            db.select(CategoryModel)
            .where(CategoryModel._id == v)
        )
        return category
    form_extra_fields = {
        "categories": SelectMultipleField(
            "categories",
            choices=list_choices,
            coerce=coerce_obj
        )
    }
    form_widget_args = {
        'desc': {
            'rows': 4,
        },
    }


class CategoryView(ModelView):
    column_list = ["_id", "name"]
    pass
