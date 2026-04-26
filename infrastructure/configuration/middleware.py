from fastapi import FastAPI

from infrastructure.configuration.log_config import RequestIDMiddleware


def configure_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestIDMiddleware)
