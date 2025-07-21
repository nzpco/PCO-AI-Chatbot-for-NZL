from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode, QueryBundle
from llama_index.core.vector_stores import MetadataFilter, FilterOperator, MetadataFilters
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores.types import MetadataInfo, VectorStoreInfo, VectorStoreQuerySpec
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.prompts import PromptTemplate
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank
from app.core.vector_store import get_vector_store
from app.core.embeddings import configure_embeddings
from app.core.llm import configure_llm
from app.core.config import get_settings
from app.db.models import LegislationFragment

class QueryEngineResponse:
    def __init__(self, answer: str, results: List[Dict[str, Any]], metadata: Dict[str, Any]):
        self.answer = answer
        self.results = results
        self.metadata = metadata

class LegislationQueryEngine:
    def __init__(self):
        # Configure embeddings and LLM
        configure_embeddings()
        configure_llm()

        # Get vector store
        self.vector_store = get_vector_store()

        # Create index from existing vector store
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)

        # Create retriever with default filters
        self.retriever = self._create_retriever()

        # Create prompt template
        self.prompt = self._create_prompt()

        # Create query engine
        self.query_engine = self._create_query_engine()

    def _create_retriever(self, fragment_type_filter: str = "Subsection", operator: FilterOperator = FilterOperator.NE) -> RetrieverQueryEngine:
        """Create a retriever with the specified filters."""
        return self.index.as_retriever(
            similarity_top_k=20,
            filters=MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="fragment_type",
                        value=fragment_type_filter,
                        operator=operator
                    )
                ]
            )
        )

    def _create_prompt(self) -> PromptTemplate:
        """Create the prompt template for the query engine."""
        return PromptTemplate(
            template="""# Legislative Navigator Prompt

You are a legislative research navigator directing users to relevant sections of New Zealand legislation based on their queries.

## User Query
{query_str}

## Retrieved Legislative Fragments
{context_str}

## Core Tasks
1. Assess each fragment's relevance to the query
2. Identify the most pertinent legislative sections
3. Create a clear roadmap to these key fragments
4. Provide minimal context for relevance
5. Maintain precise citations
6. Prioritize breadth over depth

## Response Guidelines
- Begin with a brief orientation to relevant legislative areas
- List fragments by relevance with precise citations
- Include 1-2 sentence explanations of relevance per fragment
- Include the fragment text verbatim in a markdown quote block
- Quote key phrases sparingly to aid identification
- Note connections between related fragments
- Identify potential gaps in coverage
- Avoid interpretation or definitive legal answers

## Output Format

Provide your response directly without any tags. Use markdown formatting to structure your response:

[Orientation to relevant legislative landscape]

1. [Citation]
   Relevance explanation
   > "Fragment content in markdown quote block"

2. [Citation]
   Relevance explanation
   > "Fragment content in markdown quote block"

[Note any gaps if present]"""
        )

    def _create_query_engine(self) -> RetrieverQueryEngine:
        """Create the query engine with the configured retriever and prompt."""
        settings = get_settings()
        voyageai_rerank = VoyageAIRerank(
            api_key=settings.VOYAGE_API_KEY,
            top_k=10,
            model="rerank-2",
            truncation=True
        )

        return RetrieverQueryEngine.from_args(
            retriever=self.retriever,
            response_mode=ResponseMode.SIMPLE_SUMMARIZE,
            text_qa_template=self.prompt,
            response_kwargs={
                "verbose": True,
                "similarity_threshold": 0.5
            },
            node_postprocessors=[voyageai_rerank]
        )

    async def query(self, query: str) -> QueryEngineResponse:
        """Execute a query and return the response with retrieved fragments."""
        # Get response
        response = self.query_engine.query(query)

        # Get all chunk_ids from the source nodes
        chunk_ids = [node.metadata["chunk_id"] for node in response.source_nodes]

        # Fetch all fragments in one query
        fragments = await LegislationFragment.find(
            {"chunk_id": {"$in": chunk_ids}}
        ).to_list()

        # Create a map of chunk_id to fragment for quick lookup
        fragment_map = {f.chunk_id: f for f in fragments}

        # Format retrieved fragments
        results = []
        for node in response.source_nodes:
            chunk_id = node.metadata["chunk_id"]
            fragment = fragment_map.get(chunk_id)
            if fragment:
                results.append({
                    "fragment": fragment,
                    "score": node.score if hasattr(node, 'score') else 0.0
                })

        return QueryEngineResponse(
            answer=str(response),
            results=results,
            metadata={
                "filters": {
                    "fragment_type": "not Subsection"
                },
                "query": query
            }
        )

class DocumentQueryEngine(LegislationQueryEngine):
    """Query engine specifically for searching whole documents (Acts)."""
    def __init__(self):
        super().__init__()
        # Override retriever to only search for Acts
        self.retriever = self._create_retriever("Act", FilterOperator.EQ)
        # Override prompt for document-level queries
        self.prompt = self._create_document_prompt()
        # Recreate query engine with new retriever and prompt
        self.query_engine = self._create_query_engine()

    def _create_document_prompt(self) -> PromptTemplate:
        """Create a prompt template specifically for document-level queries."""
        return PromptTemplate(
            template="""# NZ Legislative Document Navigator

You are a research assistant matching user queries to the most appropriate New Zealand legislation.

## Query
{query_str}

## Retrieved Document Summaries
{context_str}

## Important Instructions
1. You have access ONLY to document summaries, not full text
2. DO NOT invent or reference specific sections, parts, or provisions
3. Base your assessment SOLELY on the document descriptions provided
4. Use the document descriptions to determine relevance
5. A document is relevant ONLY if its core purpose relates to the query
6. Do not include information about excluded documents in your response

## Response Format

**Directly Relevant Legislation for [Query Topic]**

1. **[Act Name]**
   [Explain why this Act is relevant based ONLY on information provided in the document summary]

## Exclusion Rules
- Exclude Acts where the document summary shows no clear connection to the query
- Never mention Parts, Sections or specific provisions since you cannot verify them
- If a document summary barely mentions the query topic, exclude it
- When in doubt, exclude the document
"""
        )
