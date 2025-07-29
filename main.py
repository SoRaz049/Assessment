from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import vector_db, metadata_db
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on startup
    print("Initializing databases...")
    metadata_db.init_db()
    vector_db.init_db()
    print("Databases initialized.")
    
    yield 

    print("Application is shutting down.")

# Pass the lifespan manager to the FastAPI app instance
app = FastAPI(title="Palm Mind Technology Assessment", lifespan=lifespan)

app.include_router(api_router, prefix="/api") 

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Agent API"}