import logging
import click
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

try:
    from importlib.metadata import entry_points
except ImportError:  # pragma: no cover
    from importlib_metadata import entry_points

logger = logging.getLogger(__name__)


def get_app():
    app = FastAPI(title="LeaderBored API",openapi_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    load_modules(app)
    return app


def load_modules(app=None):
    for ep in entry_points()["leader_bored.modules"]:
        logger.info(
            "Loading module: %s",
            ep.name,
            extra={
                "color_message": "Loading module: "
                + click.style("%s", fg="cyan")
            },
        )
        mod = ep.load()
        if app:
            init_app = getattr(mod, "init_app", None)
            if init_app:
                init_app(app)
