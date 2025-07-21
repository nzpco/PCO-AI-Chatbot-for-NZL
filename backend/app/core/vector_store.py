from typing import Optional
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb import HttpClient, Settings as ChromaSettings
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)

def get_chroma_client():
    """Get or create a ChromaDB client."""
    settings = get_settings()
    return HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True, is_persistent=True)
    )

def get_vector_store(collection_name: str = "legislation") -> ChromaVectorStore:
    """Get or create a ChromaDB vector store."""
    # Initialize ChromaDB client
    chroma_client = get_chroma_client()

    # List existing collections
    existing_collections = chroma_client.list_collections()
    logger.info(f"Existing collections: {existing_collections}")

    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        configuration={
            "hnsw": {
                "space": "cosine",
                "ef_construction": 100,
                "ef_search": 100,
                "max_neighbors": 64
            }
        }
    )

    # Create and return vector store
    vector_store = ChromaVectorStore(
        chroma_collection=collection,
        store_metadata=True
    )

    return vector_store