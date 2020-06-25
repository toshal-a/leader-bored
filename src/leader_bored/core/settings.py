from secrets import token_urlsafe
from sqlalchemy.engine.url import URL, make_url
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=60 * 24 * 8)
DB_DRIVER = config("DB_DRIVER", default="postgresql+psycopg2")
DB_HOST = config("DB_HOST", default=None)
DB_PORT = config("DB_PORT", cast=int, default=None)
DB_USER = config("DB_USER", default=None)
DB_PASSWORD = config("DB_PASSWORD", cast=Secret, default=None)
DB_DATABASE = config("DB_DATABASE", default=None)
DB_DSN = config(
    "DB_DSN",
    cast=make_url,
    default=URL(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DATABASE,
    ),
)
DB_POOL_MIN_SIZE = config("DB_POOL_MIN_SIZE", cast=int, default=1)
DB_POOL_MAX_SIZE = config("DB_POOL_MAX_SIZE", cast=int, default=16)
DB_ECHO = config("DB_ECHO", cast=bool, default=False)
DB_SSL = config("DB_SSL", default=None)
DB_USE_CONNECTION_FOR_REQUEST = config(
    "DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True
)
DB_RETRY_LIMIT = config("DB_RETRY_LIMIT", cast=int, default=1)
DB_RETRY_INTERVAL = config("DB_RETRY_INTERVAL", cast=int, default=1)
PROJECT_NAME = config("PROJECT_NAME",default=None)
SECRET_KEY = config("SECRET_KEY",default=token_urlsafe(32))
SECURITY_PASSWORD_SALT=config("SECURITY_PASSWORD_SALT", default=b'CoDeDeAl')
MAIL_SERVER_HOST=config("MAIL_SERVER_HOST", default="127.0.0.1")
MAIL_SERVER_PORT=config("MAIL_SERVER_PORT", default=465)
MAIL_SENDER_EMAIL=config("MAIL_SENDER_EMAIL", default="cp-leaderboard@cp-leaderboard.me")
MAIL_SENDER_PASSWORD=config("MAIL_SENDER_PASSWORD", default="")
PROJECT_NAME=config("PROJECT_NAME", default="leaderboard")