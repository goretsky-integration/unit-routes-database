import uvicorn

from app import get_application
from config import app_settings
from db.base import Base
from db.engine import engine

app = get_application()


@app.on_event('startup')
def on_startup():
    Base.metadata.create_all(engine)


def main():
    uvicorn.run(
        'main:app',
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug,
    )


if __name__ == '__main__':
    main()
