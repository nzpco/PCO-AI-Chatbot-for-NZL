from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.vector_store import get_vector_store
from app.core.embeddings import configure_embeddings
from app.core.llm import configure_llm
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode, QueryBundle
from llama_index.core.vector_stores import MetadataFilter, FilterOperator, MetadataFilters
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores.types import MetadataInfo, VectorStoreInfo, VectorStoreQuerySpec
from llama_index.core.query_engine import RetrieverQueryEngine
from app.db.models import LegislationFragment
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core.prompts import PromptTemplate
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank
from app.core.config import get_settings
from app.core.query_engines import LegislationQueryEngine, DocumentQueryEngine, QueryEngineResponse
import json

router = APIRouter(prefix="/api/tools", tags=["tools"])

class RetrievalQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

class RetrievedFragment(BaseModel):
    fragment: LegislationFragment
    score: float

class RetrievalResponse(BaseModel):
    results: List[RetrievedFragment]
    metadata: Dict[str, Any]

class QueryEngineResponseModel(BaseModel):
    answer: str
    results: List[RetrievedFragment]
    metadata: Dict[str, Any]

@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_fragments(query: RetrievalQuery):
    """Retrieve relevant fragments using the vector index."""
    try:
        # Configure embeddings and LLM
        configure_embeddings()
        configure_llm()

        # Get vector store
        vector_store = get_vector_store()

        # Create index from existing vector store
        index = VectorStoreIndex.from_vector_store(vector_store)

        # Perform retrieval
        retriever = index.as_retriever(
            similarity_top_k=query.top_k,
            filters=MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="fragment_type",
                        value="Subsection",
                        operator=FilterOperator.NE
                    )
                ]
            )
        )
        nodes = retriever.retrieve(
            query.query,
        )

        # Get all chunk_ids from the nodes
        chunk_ids = [node.metadata["chunk_id"] for node in nodes]

        # Fetch all fragments in one query
        fragments = await LegislationFragment.find(
            {"chunk_id": {"$in": chunk_ids}}
        ).to_list()

        # Create a map of chunk_id to fragment for quick lookup
        fragment_map = {f.chunk_id: f for f in fragments}

        # Format response
        results = []
        for node in nodes:
            chunk_id = node.metadata["chunk_id"]
            fragment = fragment_map.get(chunk_id)
            if fragment:
                results.append(RetrievedFragment(
                    fragment=fragment,
                    score=node.score if hasattr(node, 'score') else 0.0
                ))

        return RetrievalResponse(
            results=results,
            metadata={
                "filters": {
                    "fragment_type": "not Subsection"
                },
                "query": query.query,
                "top_k": query.top_k
            }
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryEngineResponseModel)
async def query_legislation(query: RetrievalQuery):
    """Query the legislation using a query engine that provides both an answer and retrieved fragments."""
    try:
        # Initialize query engine
        engine = LegislationQueryEngine()

        # Get response
        response = await engine.query(query.query)

        # Convert results to RetrievedFragment format
        results = [
            RetrievedFragment(
                fragment=result["fragment"],
                score=result["score"]
            )
            for result in response.results
        ]

        return QueryEngineResponseModel(
            answer=response.answer,
            results=results,
            metadata=response.metadata
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query-documents", response_model=QueryEngineResponseModel)
async def query_documents(query: RetrievalQuery):
    """Query the legislation using a query engine that searches for whole documents (Acts) and provides both an answer and retrieved fragments."""
    try:
        # Initialize document query engine
        engine = DocumentQueryEngine()

        # Get response
        response = await engine.query(query.query)

        # Convert results to RetrievedFragment format
        results = [
            RetrievedFragment(
                fragment=result["fragment"],
                score=result["score"]
            )
            for result in response.results
        ]

        return QueryEngineResponseModel(
            answer=response.answer,
            results=results,
            metadata=response.metadata
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))