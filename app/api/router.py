from fastapi import APIRouter
from .endpoints import ingestion

api_router = APIRouter()
api_router.include_router(ingestion.router, prefix="/ingest", tags=["Ingestion"])