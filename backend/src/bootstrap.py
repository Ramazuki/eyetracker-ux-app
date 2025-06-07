from fastapi import FastAPI

from .router import apply_routers
from .exceptions import apply_exception_handlers
from .middlewares import apply_middlewares


def create_app() -> FastAPI:
    app = FastAPI()
    app = apply_routers(app)
    app = apply_middlewares(app)
    app = apply_exception_handlers(app)
    return app