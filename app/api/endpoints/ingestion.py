from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import uuid

from app.services import file_processor
from app.db import vector_db, metadata_db
from app.schemas.ingestion import UploadResponse

router = APIRouter()

def process_and_store_in_background(
    file_name: str,
    file_content: bytes,
    file_type: str,
    db: Session
):
    """The function that the background task will run."""
    print(f"Background task started for {file_name}.")
    
    # Process the file to get Document objects --> using the default 'recursive' strategy.
    documents = file_processor.process_file(
        file_name=file_name,
        file_content=file_content,
        file_type=file_type,
        chunk_strategy="recursive"
    )

    if not documents:
        print(f"No content extracted from {file_name}. Aborting storage.")
        return

    # Store the chunks and embeddings in Qdrant (Vector DB)
    vector_store = vector_db.get_vector_store()
    vector_store.add_documents(documents)
    print(f"Stored {len(documents)} chunks in Qdrant for {file_name}.")

    # Store the file metadata in PostgreSQL (Relational DB)
    metadata_db.save_file_metadata(
        db=db,
        file_name=file_name,
        chunking_strategy="recursive",
        embedding_model="all-MiniLM-L6-v2" # Default model in our vector_db service
    )
    print(f"Stored metadata in PostgreSQL for {file_name}.")
    print(f"Background task finished for {file_name}.")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(metadata_db.get_db),
):
    """
    This endpoint handles file uploads. It processes the file in the background.
    """
    if file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .pdf or .txt file.")

    # Read the file content into memory
    file_content = await file.read()

    # Create a unique ID for this processing job
    job_id = str(uuid.uuid4())

    # Add the processing function to the background tasks
    background_tasks.add_task(
        process_and_store_in_background,
        file.filename,
        file_content,
        file.content_type,
        db
    )
    
    # Return an immediate response to the user
    return {
        "message": "File upload successful. Processing in the background.",
        "file_name": file.filename,
        "job_id": job_id,
    }