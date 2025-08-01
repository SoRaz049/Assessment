# TESTING SCRIPT FOR THE SIMILARITY SEARCH ALGORITHMS IN QDRANT
import time
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Load environment variables from .env file
load_dotenv()

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
TEST_QUERY = "What programming language is used for the Helios architecture?"

def perform_test():
    """Connects to Qdrant and runs two types of searches."""
    
    if not all([QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME]):
        print("Error: Qdrant environment variables not set in .env file.")
        return

    # Initialize the client and embedding function
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"--- Testing Similarity Search Algorithms on Qdrant ---")
    print(f"Collection: '{QDRANT_COLLECTION_NAME}'")
    print(f"Query: '{TEST_QUERY}'\n")

    # Encode the test query into a vector
    query_vector = embedding_function.embed_query(TEST_QUERY)

    # TEST A: Approximate Search (HNSW Index)
    print("--- Running Test A: Approximate Search (HNSW default) ---")
    start_time_a = time.time()
    
    results_a = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=3,  # Get top 3 results
        with_payload=True # Include the document content
    )
    
    end_time_a = time.time()
    latency_a = (end_time_a - start_time_a) * 1000  # Convert to milliseconds
    
    print(f"Latency: {latency_a:.2f} ms")
    print("Results:")
    for i, hit in enumerate(results_a):
        # Cleaning up the text for readability
        payload_text = hit.payload['page_content'].replace('\n', ' ').strip()
        print(f"  {i+1}. Score: {hit.score:.4f} | Text: '{payload_text[:100]}...'")
    print("-" * 50)


    # TEST B: Exact Search (Full Scan)
    print("\n--- Running Test B: Exact Search (Full Scan) ---")
    start_time_b = time.time()
    
    results_b = client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=3,
        with_payload=True,
        # This parameter forces Qdrant to ignore the HNSW index and do a full scan
        search_params=models.SearchParams(exact=True)
    )
    
    end_time_b = time.time()
    latency_b = (end_time_b - start_time_b) * 1000  # Convert to milliseconds

    print(f"Latency: {latency_b:.2f} ms")
    print("Results:")
    for i, hit in enumerate(results_b):
        payload_text = hit.payload['page_content'].replace('\n', ' ').strip()
        print(f"  {i+1}. Score: {hit.score:.4f} | Text: '{payload_text[:100]}...'")
    print("-" * 50)

if __name__ == "__main__":
    perform_test()