# In app/schemas/ingestion.py
from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str
    file_name: str
    job_id: str