from fastapi import FastAPI

from api import routers, include_exception_handlers


def get_application() -> FastAPI:
    app = FastAPI()
    app.include_router(routers.units.router)
    app.include_router(routers.report_types.router)
    app.include_router(routers.report_routes.router)
    app.include_router(routers.telegram_chats.router)
    include_exception_handlers(app)
    return app
