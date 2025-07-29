from langchain.text_splitter import RecursiveCharacterTextSplitter
import pypdf
import io

def extract_text(file_content: bytes, file_type: str) -> str:
    """
    Extracts raw text from a file's content (bytes).
    Supports PDF and TXT files.
    """
    if file_type == "application/pdf":
        # Create a file-like object from the bytes content
        pdf_file = io.BytesIO(file_content)
        # Use pypdf to read the PDF
        pdf_reader = pypdf.PdfReader(pdf_file)
        # Join the text from all pages
        text = "".join(page.extract_text() for page in pdf_reader.pages)
    elif file_type == "text/plain":
        # Decode the bytes into a string
        text = file_content.decode("utf-8")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    return text

def chunk_text(text: str, strategy: str = "recursive", chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Chunks the given text into smaller pieces based on the chosen strategy.
    """
    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    else:
        raise ValueError(f"Unsupported chunking strategy: {strategy}")
    
    return splitter.split_text(text)