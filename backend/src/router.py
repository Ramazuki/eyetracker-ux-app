from fastapi import FastAPI

from src.apps.tracking.router import router as tracking_router
from src.apps.admin.router import router as admin_router
from src.apps.data.router import router as data_router


def apply_routers(app: FastAPI):
    app.include_router(tracking_router)
    app.include_router(admin_router)
    app.include_router(data_router)
    return app