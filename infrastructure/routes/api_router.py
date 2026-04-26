from fastapi import APIRouter

from infrastructure.routes.controller import analytics_controller, transaction_controller

router = APIRouter()
router.include_router(transaction_controller.router)
router.include_router(analytics_controller.router)
