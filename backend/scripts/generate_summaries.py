import asyncio
from typing import List
from llama_index.llms import Anthropic
from app.db.mongodb import init_mongodb
from app.db.models import LegislationFragment
from app.core.config import get_settings
from app.prompts.templates import SUMMARY_TEMPLATE, CONTEXT_SUMMARY_TEMPLATE, COMBINED_SUMMARY_TEMPLATE
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def generate_summary(text: str, fragment_type: str, llm: Anthropic, long_summary: bool = False) -> str:
    """Generate a summary of the given text using the provided LLM.
    If long_summary is False, returns only the short summary.
    If long_summary is True, returns both short and long summaries as a tuple."""
    logger.info(f"Generating {'long' if long_summary else 'short'} summary...")

    # Format the prompt using the combined template
    prompt = COMBINED_SUMMARY_TEMPLATE.format(
        fragment_type=fragment_type.lower(),
        text=text
    )

    try:
        response = await llm.acomplete(prompt)
        logger.info(f"{'Long' if long_summary else 'Short'} summary generated successfully")

        # Parse the response to extract both summaries
        response_text = response.text.strip()
        short_summary = None
        long_summary_text = None

        # Extract short summary
        if "SHORT:" in response_text:
            short_summary = response_text.split("SHORT:")[1].split("LONG:")[0].strip()

        # Extract long summary
        if "LONG:" in response_text:
            long_summary_text = response_text.split("LONG:")[1].strip()

        if long_summary:
            return short_summary, long_summary_text
        return short_summary

    except Exception as e:
        logger.error(f"Error generating {'long' if long_summary else 'short'} summary: {str(e)}")
        raise

async def get_child_fragments(parent_id: str) -> List[LegislationFragment]:
    """Get all child fragments for a given parent fragment."""
    return await LegislationFragment.find(
        LegislationFragment.parent_fragment.id == parent_id
    ).to_list()

async def get_parent_fragments(fragment_id: str) -> List[LegislationFragment]:
    """Get all parent fragments for a given fragment, ordered from root to immediate parent."""
    parents = []
    current_fragment = await LegislationFragment.get(fragment_id)

    while current_fragment and current_fragment.parent_fragment:
        parent = await current_fragment.parent_fragment.fetch()
        if parent:
            parents.insert(0, parent)  # Insert at beginning to maintain root-to-leaf order
        current_fragment = parent

    return parents

async def generate_context_summary(fragment: LegislationFragment, llm: Anthropic) -> str:
    """Generate a context summary using parent fragment summaries."""
    try:
        # Get all parent fragments
        parents = await get_parent_fragments(fragment.id)

        if not parents:
            return None

        # Build context from parent summaries
        context_parts = []
        for parent in parents:
            if parent.summary:
                context_parts.append(parent.summary)

        if not context_parts:
            return None

        # Combine parent summaries
        context_text = "\n".join(context_parts)

        # Generate context summary
        prompt = f"""Given the following context from parent sections, provide a single sentence that describes where this {fragment.fragment_type.lower()} fits in the overall document structure.

Parent section summaries:
{context_text}

Context summary:"""

        response = await llm.acomplete(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Error generating context summary for fragment {fragment.chunk_id}: {str(e)}")
        return None

async def process_content_summaries(fragment: LegislationFragment, llm: Anthropic, regenerate: bool = False) -> None:
    """Process a fragment and generate content summaries (short and long).
    For fragments > 1000 tokens, it will process children first and summarize their content.
    For fragments <= 1000 tokens, it will summarize the fragment's text directly.
    For fragments < 50 tokens, it will remove any existing summary."""
    try:
        logger.info(f"Processing content summaries for fragment: {fragment.chunk_id} ({fragment.token_count} tokens)")

        # Handle small fragments by removing their summaries
        if fragment.token_count < 50:
            if fragment.summary or fragment.summary_long:
                fragment.summary = None
                fragment.summary_long = None
                await fragment.save()
                logger.info(f"Removed summaries from small fragment {fragment.chunk_id}")
            return

        # Skip if we don't need to process this fragment
        if not regenerate and fragment.summary and fragment.summary_long:
            logger.info(f"Skipping content summaries for fragment {fragment.chunk_id} - already has summaries")
            return

        # Get child fragments
        child_fragments = await get_child_fragments(fragment.id)
        logger.info(f"Found {len(child_fragments)} child fragments")

        if fragment.token_count > 1000 and child_fragments:
            # Process each child fragment first
            for child in child_fragments:
                await process_content_summaries(child, llm, regenerate)

            # Create hierarchical summary structure
            hierarchical_text = []

            # Add parent fragment header if it has a heading
            if fragment.heading:
                header = f"# {fragment.descriptive_label}: {fragment.heading}"
            else:
                header = f"# {fragment.descriptive_label}"

                hierarchical_text.append(header)
                hierarchical_text.append("")  # Empty line after header

            # Add child fragments in hierarchical structure
            for child in child_fragments:
                # Add child header with label if available
                child_header = f"  - {child.descriptive_label}:"
                if child.heading:
                    child_header += f": {child.heading}"
                hierarchical_text.append(child_header)

                # Add child summary or text, indented
                if child.summary:
                    hierarchical_text.append(f"     {child.summary}")
                else:
                    # If no summary, use the text
                    hierarchical_text.append(f"     {child.text}")
                hierarchical_text.append("")  # Empty line between children

            # Join all parts with newlines
            combined_text = "\n".join(hierarchical_text)

            # Generate both summaries for the hierarchical structure in one call
            summary, summary_long = await generate_summary(combined_text, fragment.fragment_type, llm, long_summary=True)
        else:
            # For smaller fragments or those without children, summarize directly
            # Only generate long summary for fragments with more than 500 tokens
            if fragment.token_count > 500:
                summary, summary_long = await generate_summary(fragment.text, fragment.fragment_type, llm, long_summary=True)
            else:
                summary = await generate_summary(fragment.text, fragment.fragment_type, llm, long_summary=False)
                summary_long = None

        # Update fragment with summaries
        fragment.summary = summary
        fragment.summary_long = summary_long
        await fragment.save()

        logger.info(f"Successfully generated and saved content summaries for {fragment.chunk_id}")

        # Add a small delay to avoid rate limits
        await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error processing content summaries for fragment {fragment.chunk_id}: {str(e)}")

async def process_context_summaries(fragment: LegislationFragment, llm: Anthropic, regenerate: bool = False, parent_fragments: List[LegislationFragment] = None) -> None:
    """Process a fragment and generate context summaries.
    This should be called after all content summaries are generated.

    Args:
        fragment: The fragment to process
        llm: The LLM to use for generation
        regenerate: Whether to regenerate existing summaries
        parent_fragments: List of parent fragments, ordered from root to immediate parent
    """
    try:
        logger.info(f"Processing context summary for fragment: {fragment.chunk_id}")

        # Skip if we don't need to process this fragment
        if not regenerate and fragment.summary_context:
            logger.info(f"Skipping context summary for fragment {fragment.chunk_id} - already has context")
            return

        # Generate context summary using parent fragments
        if parent_fragments:
            # Format each parent's information with heading and label
            context_parts = []
            for parent in parent_fragments:
                if parent.summary:
                    if parent.heading and parent.descriptive_label:
                        heading = f"{parent.descriptive_label}: {parent.heading}"
                    elif parent.descriptive_label:
                        heading = f"{parent.descriptive_label}"
                    else:
                        heading = ""
                    text = parent.summary if parent.summary else parent.text
                    context_parts.append(f"  - {heading}\n{text}")

            if context_parts:
                context_text = "\n\n".join(context_parts)
                text = fragment.summary if fragment.summary else fragment.text
                # Use the new template for context summary generation
                prompt = CONTEXT_SUMMARY_TEMPLATE.format(
                    fragment_type=fragment.fragment_type.lower(),
                    heading=f"{fragment.descriptive_label}: {fragment.heading}" if fragment.heading else f"{fragment.descriptive_label}",
                    content=text,
                    chunk_id=fragment.chunk_id,
                    parent_summaries_list=context_text
                )


                response = await llm.acomplete(prompt)
                context_summary = response.text.strip()

                if context_summary:
                    fragment.summary_context = context_summary
                    await fragment.save()
                    logger.info(f"Successfully generated and saved context summary for {fragment.chunk_id}")

        # Get child fragments
        child_fragments = await get_child_fragments(fragment.id)

        # Create new context chain including this fragment for all children
        child_context = parent_fragments.copy() if parent_fragments else []
        child_context.append(fragment)

        # Process all children with the same context chain
        for child in child_fragments:
            if child.fragment_type not in ["LabelPara", "Notes"]:
                await process_context_summaries(child, llm, regenerate, child_context)

        # Add a small delay to avoid rate limits
        await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error processing context summary for fragment {fragment.chunk_id}: {str(e)}")

async def get_root_fragments(document_id: str = None) -> List[LegislationFragment]:
    """Get root fragments (those without parents) for a document."""
    query = {"parent_fragment.$id": None}
    if document_id:
        query["document.$id"] = document_id
    return await LegislationFragment.find(query).to_list()

async def process_fragments(regenerate: bool = False, document_id: str = None):
    """Process legislation fragments and generate summaries in two phases:
    1. Generate content summaries (bottom-up)
    2. Generate context summaries (top-down)"""
    logger.info("Starting summary generation process...")

    # Initialize database connection
    logger.info("Initializing database connection...")
    await init_mongodb()
    logger.info("Database connection initialized")

    # Initialize Anthropic LLM
    logger.info("Initializing Anthropic LLM...")
    settings = get_settings()
    llm = Anthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        model="claude-3-haiku-20240307",
        temperature=0.1  # Lower temperature for more focused summaries
    )
    logger.info("LLM initialized successfully")

    # Get root fragments (those without parents)
    root_fragments = await get_root_fragments(document_id)
    logger.info(f"Found {len(root_fragments)} root fragments")

    if not root_fragments:
        logger.info("No root fragments found. Exiting.")
        return

    # Phase 1: Generate content summaries (bottom-up)
    logger.info("Starting Phase 1: Generating content summaries...")
    for i, fragment in enumerate(root_fragments, 1):
        try:
            logger.info(f"Processing root fragment {i}/{len(root_fragments)}: {fragment.chunk_id} ({fragment.token_count} tokens)")
            await process_content_summaries(fragment, llm, regenerate)
        except Exception as e:
            logger.error(f"Error processing root fragment {fragment.chunk_id}: {str(e)}")

    # Phase 2: Generate context summaries (top-down)
    logger.info("Starting Phase 2: Generating context summaries...")
    for i, fragment in enumerate(root_fragments, 1):
        try:
            logger.info(f"Processing root fragment {i}/{len(root_fragments)}: {fragment.chunk_id}")
            # Start with empty parent fragments for root fragments
            await process_context_summaries(fragment, llm, regenerate, [])
        except Exception as e:
            logger.error(f"Error processing root fragment {fragment.chunk_id}: {str(e)}")

    logger.info("Summary generation completed successfully")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Generate summaries for legislation fragments')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate existing summaries')
    parser.add_argument('--document-id', type=str, help='Process only fragments from this document ID')
    args = parser.parse_args()

    try:
        logger.info("Starting summary generation script...")
        asyncio.run(process_fragments(regenerate=args.regenerate, document_id=args.document_id))
        logger.info("Summary generation completed successfully")
    except Exception as e:
        logger.error(f"Error during summary generation: {str(e)}")
    finally:
        # Close any open connections
        pass

if __name__ == "__main__":
    main()