
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, tickets
from app.db.database import Base, engine
from app.models.ticket import Ticket


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SupportIQ",
    description="AI-powered customer support ticket analyzer",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
