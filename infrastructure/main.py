import logging.config

from fastapi import FastAPI

# from infrastructure.configuration.log_config import LOGGING_CONFIG
# from infrastructure.configuration.middleware import configure_middleware
from infrastructure.routes.api_router import router
from infrastructure.settings.settings import settings

# logging.config.dictConfig(LOGGING_CONFIG)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    # configure_middleware(app)
    app.include_router(router)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
