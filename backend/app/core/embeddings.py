from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.core import Settings
from app.core.config import get_settings
import voyageai
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank

def configure_embeddings() -> None:
    """Configure the embedding model for LlamaIndex."""
    settings = get_settings()

    # Set API key directly in VoyageAI module
    voyageai.api_key = settings.VOYAGE_API_KEY

    # Initialize VoyageAI embedding model
    embed_model = VoyageEmbedding(
        model_name="voyage-law-2"
    )

    # Configure LlamaIndex settings
    Settings.embed_model = embed_model