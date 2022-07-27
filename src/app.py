from fastapi import FastAPI

import routers
from db import redis_db, mongo_db

app = FastAPI()
app.include_router(routers.auth.router)
app.include_router(routers.units.router)
app.include_router(routers.reports.router)
app.include_router(routers.accounts.router)
app.include_router(routers.report_types.router)
app.include_router(routers.ping.router)


@app.on_event('startup')
async def on_startup():
    await redis_db.ping()


@app.on_event('shutdown')
async def on_shutdown():
    await redis_db.close_connection()
    mongo_db.close_connection()
