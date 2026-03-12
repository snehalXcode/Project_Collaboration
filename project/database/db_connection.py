import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


# Use naming convention so migrations (if added later) are easier.
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


def build_mysql_uri() -> str:
    """
    Build a MySQL connection URI from environment variables.

    Environment variables:
    - DB_USER (default: ngo_user)
    - DB_PASSWORD (default: strong_password_here)
    - DB_HOST (default: localhost)
    - DB_NAME (default: ngo_animals)
    """
    user = os.getenv("DB_USER", "ngo_user")
    password = os.getenv("DB_PASSWORD", "strong_password_here")
    host = os.getenv("DB_HOST", "localhost")
    name = os.getenv("DB_NAME", "ngo_animals")

    return f"mysql+pymysql://{user}:{password}@{host}/{name}"


def init_app(app):
    """
    Configure the Flask app with SQLAlchemy and initialize the db object.
    """
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", build_mysql_uri())
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)

