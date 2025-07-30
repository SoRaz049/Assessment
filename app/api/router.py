from fastapi import APIRouter
from .endpoints import ingestion, agent

api_router = APIRouter()
api_router.include_router(ingestion.router, prefix="/ingest", tags=["Ingestion"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])