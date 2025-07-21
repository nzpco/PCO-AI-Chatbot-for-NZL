from llama_index.core import Settings
from llama_index.llms.anthropic import Anthropic
from app.core.config import get_settings

def configure_llm():
    """Configure global LLM settings for LlamaIndex."""
    settings = get_settings()

    # Configure Anthropic LLM
    llm = Anthropic(
        model="claude-3-haiku-20240307",
        api_key=settings.ANTHROPIC_API_KEY,
        temperature=0.1,
    )

    # Set global settings
    Settings.llm = llm