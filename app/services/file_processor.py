import io
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_experimental.text_splitter import SemanticChunker

from app.db.vector_db import get_embedding_function

def process_file(
    file_name: str, 
    file_content: bytes, 
    file_type: str, 
    chunk_strategy: str = "semantic"
) -> list[Document]:
    """
    The main orchestrator function.
    Takes file details, extracts text, chunks it, and returns a list of Document objects.
    """
    # Extract raw text from the file content
    raw_text = _extract_text_from_bytes(file_content, file_type)
    
    if not raw_text:
        return []

    # Chunk the text into Document objects
    documents = _chunk_text_to_documents(raw_text, file_name, chunk_strategy)
    
    print(f"Successfully processed and chunked '{file_name}' into {len(documents)} documents.")
    return documents


# Helper Functions
def _extract_text_from_bytes(file_content: bytes, file_type: str) -> str:
    """
    Extracts raw text from in-memory file content (bytes).
    """
    if file_type == "application/pdf":
        pdf_file = io.BytesIO(file_content)
        reader = pypdf.PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in reader.pages)
    elif file_type == "text/plain":
        text = file_content.decode("utf-8")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    return text


def _chunk_text_to_documents(
    text: str, 
    file_name: str, 
    strategy: str
) -> list[Document]:
    """
    Chunks the text using either a recursive or semantic strategy.
    """
    if strategy == "semantic":
        # Use SemanticChunker. It requires the embedding model.
        # By default, it uses a percentile threshold, which is robust.
        embeddings = get_embedding_function()
        text_splitter = SemanticChunker(embeddings)
    elif strategy == "recursive":
        # Fallback to our previous recursive method if specified
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, # Using the smaller size we tested
            chunk_overlap=100,
            length_function=len,
        )
    else:
        raise ValueError(f"Unsupported chunking strategy: {strategy}")

    # Create the documents. SemanticChunker has a `create_documents` method
    # that is very convenient.
    documents = text_splitter.create_documents([text])
    
    # We can add the source metadata to each document for traceability
    for doc in documents:
        doc.metadata["source"] = file_name
        
    print("\n" + "="*50)
    print("--- DEBUG: GENERATED CHUNKS ---")
    for i, doc in enumerate(documents):
        print(f"\n--- CHUNK {i+1} ---")
        print(doc.page_content)
        print("-"*(len(f"--- CHUNK {i+1} ---")))
    print("="*50 + "\n")
    
    return documents
