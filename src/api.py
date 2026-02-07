from fastapi import APIRouter

from src.auth.routers import router as auth_router
from src.bookings.routers import router as bookings_router
from src.tables.routers import router as tables_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tables_router)
api_router.include_router(bookings_router)
