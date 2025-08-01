
# Backend RAG Agent Assessment

This project is a backend system designed to demonstrate a comprehensive Retrieval-Augmented Generation (RAG) pipeline.

## Overview

The system consists of a FastAPI backend with two primary APIs:

1. **`/api/ingest/upload`**: Handles file uploads (`.pdf`, `.txt`), extracts text, chunks it using configurable strategies, generates embeddings, and stores them in a Qdrant vector database. All file metadata is stored in a PostgreSQL database.
2. **`/api/agent/chat`**: Implements a RAG-based agentic system using LangChain. The agent uses tools to answer user queries based on the ingested documents and can handle an interview booking process. Conversational memory is maintained using Redis.

## Architecture

The system is composed of several containerized services managed by Docker Compose, ensuring a clean and reproducible environment:

- **FastAPI Application**: The core Python backend handling all API logic.
- **Qdrant**: The vector database for storing and searching document embeddings.
- **PostgreSQL**: The relational database for storing metadata and interview bookings.
- **Redis**: The in-memory data store for managing conversational chat history.
- **Google Gemini**: The LLM used by the LangChain agent for reasoning and generation.

## Features

- [X] **Two RESTful APIs** using FastAPI.
- [X] **File Ingestion**: Supports `.pdf` and `.txt` uploads.
- [X] **Advanced Chunking**: Implemented both Recursive and Semantic chunking strategies.
- [X] **Vector Storage**: Uses Qdrant for storing embeddings.
- [X] **Metadata Storage**: Uses PostgreSQL for file and booking metadata.
- [X] **Agentic System**: Built with LangChain, using tools for reasoning.
- [X] **Conversational Memory**: Implemented with Redis for context-aware conversations.
- [X] **Interview Booking**: A dedicated tool captures user details, saves them to PostgreSQL, and sends a confirmation email via SMTP.
- [X] **Clean, Modular Code**: The project follows a structured and production-ready file layout.
- [X] **Comparative Analysis**: Two reports detailing findings on chunking/embedding strategies and similarity search algorithms are included.

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **AI/ML**: LangChain, LangChain Experimental, Google Gemini
- **Databases**: Qdrant (Vector), PostgreSQL (Relational), Redis (Cache/Memory)
- **Containerization**: Docker, Docker Compose
- **Other Libraries**: SQLAlchemy, Pydantic, python-dotenv, psycopg2

## Setup and Installation

### Prerequisites

- Git
- Docker and Docker Compose
- Python 3.10+

### 1. Clone the Repository

```bash
git clone https://github.com/SoRaz049/Assessment.git
cd Assessment
```

### 2. Configure Environment Variables

- Create a `.env` file in the root directory.
- TRY REPLACING API KEY, EMAIL AND PASSWORD. OTHER DETAILS CAN REMAIN SAME.

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/palm_mind_db

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=palm_mind_collection

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM
GOOGLE_API_KEY="YOUR_API_KEY"

# Email (for booking notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER_EMAIL=YOUR_EMAIL
SMTP_SENDER_PASSWORD=YOUR APP PASSWORD  #(to get the app password use this: https://myaccount.google.com/apppasswords)

```

### 3. Start the Backend Services

This command will start the Qdrant, PostgreSQL, and Redis containers in the background.

```bash
docker-compose up -d
```

### 4. Set Up the Python Environment

Create a virtual environment and install the required packages.

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
source .venv\Scripts\activate

# Activate it (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## API Usage

Navigate to `http://localhost:8000/docs` to access the interactive Swagger UI for testing the API endpoints.

### 1. Ingest a Document

- Go to the `POST /api/ingest/upload` endpoint.
- Click "Try it out".
- Upload a `.pdf` or `.txt` file.
- Click "Execute".
- The file will be processed in the background. Check your terminal for logs.

### 2. Chat with the Agent

- Go to the `POST /api/agent/chat` endpoint.
- Click "Try it out".
- Provide a unique `session_id` to maintain conversation history.
- Provide a `query`.

**Example Q&A:**

```json
{
  "query": "What is the main idea of the document?",
  "session_id": "session_123"
}
```

**Example Interview Booking:**

```json
{
  "query": "I want to book an interview for Swaraj Kumar, email swaraj@example.com, for tomorrow at 3 PM.",
  "session_id": "session_456"
}
```

## Future Improvements

This project provides a solid foundation for a production-grade RAG system. Several areas could be enhanced further:

1. **Hybrid Search**: Implement a hybrid search mechanism that combines keyword-based search (like BM25) with the current semantic vector search. This would improve retrieval for queries containing specific jargon, acronyms, or codes that embedding models might miss.
2. **Advanced Retrieval Strategies**:

   * **Contextual Compression**: Implement a compression step after retrieval where an LLM filters the retrieved chunks to only pass the most relevant sentences to the final generation prompt, reducing noise and context window usage.
   * **Re-ranking**: Use a more powerful, cross-encoder model to re-rank the top N documents returned by the initial retriever for even higher accuracy.
3. **Agent & Tool Enhancements**:

   * **LangGraph Implementation**: For more complex workflows (e.g., booking an interview that requires checking a calendar for availability first), the agent could be re-implemented using LangGraph to create a more explicit state machine for its reasoning process.
   * **Asynchronous Tools**: Convert the tool's `_run` methods to `_arun` methods to make them fully asynchronous, improving the overall performance and concurrency of the FastAPI application.
4. **Observability and Evaluation**:

   * **Tracing**: Integrate a tool like LangSmith or Arize AI to trace the agent's decision-making process, evaluate the quality of retrievals and generations, and identify failure points.
   * **Automated Evaluation**: Build a quantitative evaluation pipeline using a "golden dataset" of questions and answers to automatically score the performance of different system configurations (e.g., using RAGAs).
5. **Robust PDF Processing**: The current `pypdf` library is effective for simple text extraction. For complex PDFs with tables, images, and multi-column layouts, integrating a more advanced parsing tool like `LlamaParse` or `unstructured.io` would significantly improve the quality of the initial text extraction.

---
