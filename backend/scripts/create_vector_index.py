import asyncio
import logging
from app.db.mongodb import init_mongodb
from app.db.models import LegislationFragment
from app.core.index import create_nodes_from_fragments, create_legislation_index
from app.core.vector_store import get_chroma_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_index():
    """Load documents and create vector index."""
    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        await init_mongodb()
        logger.info("Database connection initialized")

        # Get all fragments except LabelPara and Notes
        logger.info("Loading fragments from database...")
        fragments = await LegislationFragment.find(
            {"fragment_type": {"$nin": ["LabelPara", "Notes"]}}
        ).to_list()
        logger.info(f"Loaded {len(fragments)} fragments")

        # Create nodes from fragments
        logger.info("Creating nodes from fragments...")
        nodes = create_nodes_from_fragments(fragments)
        logger.info(f"Created {len(nodes)} nodes")

        # Create index
        logger.info("Creating vector index...")
        index = create_legislation_index(nodes)
        logger.info("Vector index created successfully")

    except Exception as e:
        logger.error(f"Error creating vector index: {str(e)}")
        raise
    finally:
        # Close any open connections
        pass

def main():
    """Main entry point for the script."""
    asyncio.run(create_index())

if __name__ == "__main__":
    main()