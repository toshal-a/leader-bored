from . import db
from sqlalchemy import Enum


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger(), primary_key=True)
    full_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    hashed_password = db.Column(db.String(), nullable=False)
    current_class = db.Column(
        Enum('fe', 'se', 'te', 'be', 'other', name="ClassEnum"),
        nullable=False,
        default='be',
        server_default='be'
    )
    codeforces_handle = db.Column(db.String(), nullable=False)
    rank = db.Column(db.Integer(), default=None)
