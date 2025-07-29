import io
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

def process_file(
    file_name: str, 
    file_content: bytes, 
    file_type: str, 
    chunk_strategy: str = "recursive"
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
    strategy: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200
) -> list[Document]:
    """
    Chunks the text and creates LangChain Document objects, including metadata.
    """
    if strategy == "recursive":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    else:
        raise ValueError(f"Unsupported chunking strategy: {strategy}")

    # Split the text into chunks of strings first
    chunks = text_splitter.split_text(text)
    
    # Now, create a Document object for each chunk with the source filename as metadata
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": file_name,
                "chunk_number": i
            }
        )
        documents.append(doc)
        
    return documents