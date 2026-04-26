import logging

from fastapi.responses import JSONResponse


def register_exception_handlers(app):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc):
        logging.error("An unhandled exception occurred", exc_info=True, extra={"traceback": True})
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )