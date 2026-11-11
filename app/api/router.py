from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.tickets.router import router as tickets_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(tickets_router)