import uvicorn

from app import app
from config import get_app_settings


def main():
    app_settings = get_app_settings()
    uvicorn.run(
        'app:app',
        debug=app_settings.debug,
        host=app_settings.host,
        port=app_settings.port,
    )


if __name__ == '__main__':
    main()
