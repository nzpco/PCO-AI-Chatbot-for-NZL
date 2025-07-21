# Backend (FastAPI)

This is the backend for the Chat-Based Access to Legislation project. It provides API endpoints and RAG (Retrieval-Augmented Generation) functionality for the chatbot and search tools.

## Requirements
- Python 3.10+
- Poetry (for dependency management)

## Running the Backend
```bash
cd backend
poetry install
poetry shell
uvicorn main:app --reload
```
The API will be available at http://localhost:8000/docs 