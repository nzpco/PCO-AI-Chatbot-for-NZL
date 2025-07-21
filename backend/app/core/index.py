from typing import List
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo
from llama_index.core.storage import StorageContext
from app.db.models import LegislationFragment
from app.core.vector_store import get_vector_store
from app.core.llm import configure_llm
from app.core.embeddings import configure_embeddings

def create_legislation_index(nodes: List[TextNode]) -> VectorStoreIndex:
    """Create a vector index from provided nodes."""
    # Configure LLM settings
    configure_llm()
    configure_embeddings()

    # Get vector store
    vector_store = get_vector_store()

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    try:
        vector_store.clear()
    except Exception:
        # Ignore error if store is already empty
        pass

    # Create index with pre-computed embeddings
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        transformations=[],  # No transformations needed since embeddings are pre-computed
        show_progress=True,
        insert_batch_size=1024,
    )

    return index

def create_nodes_from_fragments(fragments: List[LegislationFragment]) -> List[TextNode]:
    """Create TextNodes from a list of LegislationFragments."""
    nodes = []
    for fragment in fragments:
        # Create the same combined text format used for embedding generation
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

        combined_text = "\n".join(parts)

        # Create text node with pre-computed embedding
        node = TextNode(
            id=fragment.chunk_id,
            text=combined_text,
            embedding=fragment.embedding,
            metadata={
                "chunk_id": fragment.chunk_id,
                "fragment_type": fragment.fragment_type,
                "descriptive_label": fragment.descriptive_label,
                "fragment_label": fragment.fragment_label,
                "heading": fragment.heading,
                "summary": fragment.summary,
                "act_name": fragment.act_name,
                "act_number": fragment.act_number,
                "act_year": fragment.act_year,
                "schedule_label": fragment.schedule_label,
                "schedule_name": fragment.schedule_name,
                "part_label": fragment.part_label,
                "part_name": fragment.part_name,
                "subpart_label": fragment.subpart_label,
                "subpart_name": fragment.subpart_name,
                "crosshead_name": fragment.crosshead_name,
                "section_label": fragment.section_label,
                "section_name": fragment.section_name,
                "paragraph_label": ' '.join(fragment.paragraph_label),
                "token_count": fragment.token_count,
                "document_id": str(fragment.document.ref.id) if fragment.document else None,
                "parent_id": str(fragment.parent_fragment.ref.id) if fragment.parent_fragment else None
            }
        )

        # Add parent relationship if exists
        if fragment.parent_fragment.ref.id:
            node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(node_id=str(fragment.parent_fragment.ref.id))

        nodes.append(node)

    return nodes