import asyncio
import logging
import argparse
from typing import List
from tqdm import tqdm

from app.db.mongodb import init_mongodb
from app.db.models import LegislationFragment
from app.core.embeddings import configure_embeddings
from llama_index.core import Document, Settings
from llama_index.core.schema import TextNode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_combined_text(fragment: LegislationFragment) -> str:
    """Create a combined text for embedding that includes key information."""
    parts = []

    # Add chunk ID
    parts.append(f"[{fragment.chunk_id}]")

    # Add label and heading
    label_parts = []
    if fragment.descriptive_label:
        label_parts.append(fragment.descriptive_label)
    if fragment.heading:
        label_parts.append(fragment.heading)
    if label_parts:
        parts.append(": ".join(label_parts))

    # Add context summary if available
    if fragment.summary_context:
        parts.append(fragment.summary_context)

    # Add detailed content, preferring text if under 1000 tokens, otherwise use summary_long
    if fragment.text and len(fragment.text.split()) <= 1000:
        parts.append(fragment.text)
    elif fragment.summary_long:
        parts.append(fragment.summary_long)
    else:
        # Fallback: truncate text if both above conditions fail
        text = fragment.text
        words = text.split()
        if len(words) > 1000:
            text = " ".join(words[:1000]) + "..."
        parts.append(text)

    return "\n".join(parts)

def create_nodes_for_embedding(fragments: List[LegislationFragment]) -> List[TextNode]:
    """Create nodes for embedding generation."""
    nodes = []
    for fragment in fragments:
        combined_text = create_combined_text(fragment)
        nodes.append(TextNode(
            text=combined_text,
            metadata={
                "chunk_id": fragment.chunk_id
            }
        ))
    return nodes

async def populate_embeddings(document_id: str = None, batch_size: int = 100):
    """Populate embeddings for all legislation fragments.

    Args:
        document_id: Optional document ID to filter fragments by
        batch_size: Number of texts to embed in each batch
    """
    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        await init_mongodb()
        logger.info("Database connection initialized")

        # Configure embeddings
        logger.info("Configuring embeddings...")
        configure_embeddings()
        logger.info("Embeddings configured")

        # Get all fragments, optionally filtered by document_id
        logger.info("Loading fragments from database...")
        query = {}
        if document_id:
            query["document.$id"] = document_id
            logger.info(f"Filtering fragments for document ID: {document_id}")

        fragments = await LegislationFragment.find(query).to_list()
        logger.info(f"Loaded {len(fragments)} fragments")

        # Create nodes for embedding
        logger.info("Creating nodes for embedding...")
        nodes = create_nodes_for_embedding(fragments)
        logger.info(f"Created {len(nodes)} nodes for embedding")

        # Create a map of chunk_id to fragment for quick lookup
        fragment_map = {f.chunk_id: f for f in fragments}

        # Process nodes in batches
        logger.info(f"Generating embeddings in batches of {batch_size}...")
        for i in tqdm(range(0, len(nodes), batch_size), desc="Processing batches"):
            batch_nodes = nodes[i:i + batch_size]
            batch_texts = [node.text for node in batch_nodes]

            # Generate embeddings for the batch
            batch_embeddings = Settings.embed_model.get_text_embedding_batch(batch_texts)

            # Update fragments with their embeddings
            for node, embedding in zip(batch_nodes, batch_embeddings):
                chunk_id = node.metadata["chunk_id"]
                fragment = fragment_map.get(chunk_id)

                if fragment:
                    fragment.embedding = embedding
                    await fragment.save()

        logger.info("Embeddings populated successfully")

    except Exception as e:
        logger.error(f"Error populating embeddings: {str(e)}")
        raise

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Populate embeddings for legislation fragments')
    parser.add_argument('--document-id', type=str, help='Process only fragments from this document ID')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of texts to embed in each batch')
    args = parser.parse_args()

    try:
        logger.info("Starting embeddings population script...")
        asyncio.run(populate_embeddings(document_id=args.document_id, batch_size=args.batch_size))
        logger.info("Embeddings population completed successfully")
    except Exception as e:
        logger.error(f"Error during embeddings population: {str(e)}")
    finally:
        # Close any open connections
        pass

if __name__ == "__main__":
    main()