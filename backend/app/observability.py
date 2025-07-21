import os
import logging

logger = logging.getLogger(__name__)

from app.core.config import get_settings
from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

def init_observability():
    settings = get_settings()
    logger.info(f"Initializing observability with Phoenix API key: {settings.PHOENIX_API_KEY}")
    os.environ["PHOENIX_API_KEY"] = settings.PHOENIX_API_KEY
    tracer_provider = register(
        project_name="pco-chatbot-rnd2", # Default is 'default'
        endpoint="https://pco-chatbot-rnd-phoenix.cloud.boost.co.nz/v1/traces",
        auto_instrument=True # Auto-instrument your app based on installed dependencies
    )

    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
