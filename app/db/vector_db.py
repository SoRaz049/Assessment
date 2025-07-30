from qdrant_client import QdrantClient, models
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.core.config import settings
from langchain_community.vectorstores import Qdrant

_qdrant_client = None
_embedding_function = None

def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client

def get_embedding_function():
    global _embedding_function
    if _embedding_function is None:
        # Initialize the embedding function with a specific model
        _embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embedding_function

def init_db():
    client = get_qdrant_client()
    embedding_size = get_embedding_function().client.get_sentence_embedding_dimension()
    
    # Check if the collection already exists
    try:
        client.get_collection(collection_name=settings.QDRANT_COLLECTION_NAME)
        print("Qdrant collection already exists.")
    except Exception:
        # If it doesn't exist, create it
        print("Creating Qdrant collection.")
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(size=embedding_size, distance=models.Distance.COSINE),
        )

def get_vector_store() -> Qdrant:
    """
    Returns a LangChain Qdrant vector store instance.
    This is the main object we use to interact with Qdrant via LangChain.
    """
    client = get_qdrant_client()
    embeddings = get_embedding_function()
    
    vector_store = Qdrant(
        client=client,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        embeddings=embeddings,
    )
    return vector_store
