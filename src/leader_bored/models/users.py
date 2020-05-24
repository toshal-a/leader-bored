from . import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger(), primary_key=True)
    full_name = db.Column(db.String(),nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    hashed_password = db.Column(db.String(), nullable=False)
    codeforces_handle = db.Column(db.String(), nullable=False)
    rank = db.Column(db.Integer(), default=None)