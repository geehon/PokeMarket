if __name__ == "__main__":
    print("This is the main file")
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import User, Pokemon, Cart

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {"sa": sa, "so": so, "db": db,
            "U": User, "P": Pokemon, "C": Cart}
