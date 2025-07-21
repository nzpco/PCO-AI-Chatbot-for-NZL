from typing import List, Dict, Any, Optional, Tuple
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import BaseTool
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage
from app.core.llm import configure_llm
from app.core.embeddings import configure_embeddings
from app.core.vector_store import get_vector_store
from app.db.models import LegislationFragment
from app.core.index import create_nodes_from_fragments
from app.core.query_engines import LegislationQueryEngine, DocumentQueryEngine

class LegislationReActAgent:
    def __init__(self):
        # Configure LLM and embeddings
        self.llm = configure_llm()
        configure_embeddings()

        # Get vector store and create index from existing vector store
        vector_store = get_vector_store()
        self.index = VectorStoreIndex.from_vector_store(vector_store)

        # Create debug handler
        debug_handler = LlamaDebugHandler(print_trace_on_end=True)
        callback_manager = CallbackManager([debug_handler])

        # Create tools
        self.tools = self._create_tools()

        # Create the agent with system prompt
        self.agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            callback_manager=callback_manager,
            verbose=True,
#             context="""You are a helpful AI assistant specialized in handling legislation-related queries.
# Your primary role is to help users understand and navigate through legislation by:
# 1. Answering specific questions about legislation sections and parts
# 2. Providing information about relevant Acts and their contents
# 3. Explaining legal concepts and terminology in clear, accessible language

# You have access to tools to search the legislation.
# Do not answer questions using trained knowledge of legislation, only use information you can find using the tools.

# If you can't find the information using the tools, say you don't know.

# When responding:
# - Be precise and accurate in your answers
# - Use the legislation to answer questions rather than making assertions about the users situation
# - Cite specific fragments of legislation that back up your answers
# - Always reference where in legislation the answer can be found
# - Explain complex legal terms in simple language
# - If you're unsure about something, acknowledge the uncertainty
# - Always maintain a professional and helpful tone

# You MUST use the provided tools to answer questions about New Zealand legislation.
# Your training data is outdated and could be inaccurate. Even if you believe you know the answer,
# you MUST verify it by searching the knowledge base. Any response about New Zealand legislation not
# supported by a tool call will be considered incorrect.

# You MUST cite where in legislation the answer can be found.
# """
            context="""
You are an AI assistant designed to be a legislation research tool for New Zealand's legislation.
You are part of a website provided by the Parliamentary Council Office. Your purpose is to find answers to users' questions about legislation using the provided tools.
You must strictly avoid offering legal interpretation of the legislation or making assertions about the user's situation or the outcome of legal cases.

You have access to a database of New Zealand legislation that you should use to find the answer for the users question.
Use the query_index tool to retrieve sections of legislation that are relevant to the users question, do not rely on prior knowledge.

As a public servant and a representative of the Parliamentary Counsel Office, you should:
- Avoid making legal interpretations of the legislation, only use the legislation to answer the users question.
- Avoid making judgement about what the law means or how it applies to the users situation, instead help the user find the relevant legislation.
- Avoid making predictions about the outcome of a legal case or what a court would rule.
- Do not provide general advice, unless it is based on legislation retrieved from the database.
- Assume that the user is asking a question that can be answered by New Zealand legislation.
- You may need to reword the users question to be more specific to legislation.
- Answer in english, do not use any other language.
- If the task is not answering a question about New Zealand legislation, decline to answer politely.
- If you cannot find a clear answer, admit that you don't know or that the information is not available in the legislation you have access to.
- Cite specific fragments of legislation that back up your answers
- Always reference where in legislation the answer can be found

You MUST use the provided tools to answer questions about New Zealand legislation.
Your training data is outdated and could be inaccurate. Even if you believe you know the answer,
you MUST verify it by searching the knowledge base. Any response about New Zealand legislation not
supported by a tool call will be considered incorrect.

You MUST cite where in legislation the answer can be found.

Do NOT generate observations you have not been given.

The current year is 2025."""
        )

    def _create_tools(self) -> List[BaseTool]:
        """Create the tools for the agent."""
        return [
            self._create_legislation_query_tool(),
            self._create_document_query_tool()
        ]

    def _create_legislation_query_tool(self) -> BaseTool:
        """Create a tool for querying legislation fragments."""
        from llama_index.core.tools import FunctionTool

        async def query_legislation(query: str) -> str:
            """Query the legislation index and get a response."""
            engine = LegislationQueryEngine()
            response = await engine.query(query)
            return response.answer

        return FunctionTool.from_defaults(
            fn=query_legislation,
            name="query_legislation_fragments",
            description="""Query an index containing the contents of New Zealand legislation. Use this to read parts of the legislation relevant to the query.
            The input query is used to find semantically similar fragments from the index, and a response is returned with the most relevant sections.
            Input should be a question about specific sections or parts of legislation.
            All documents are from New Zealand legislation so don't include "new zealand" in your query.
            """
        )

    def _create_document_query_tool(self) -> BaseTool:
        """Create a tool for querying whole documents (Acts)."""
        from llama_index.core.tools import FunctionTool

        async def query_documents(query: str) -> str:
            """Query the legislation index and get a response about whole documents."""
            engine = DocumentQueryEngine()
            response = await engine.query(query)
            return response.answer

        return FunctionTool.from_defaults(
            fn=query_documents,
            name="query_documents",
            description="""Query an index containing entries for each legislative Act that this chatbot has access to.
            The input query is used to find semantically similar documents from the index, and a response is returned with the most relevant documents.
            Input should be a question about which Acts are relevant to a topic.
            All documents are from New Zealand legislation so don't include "new zealand" in your query unless it's part of the question."""
        )

    async def chat(self, message: str, chat_history: List[ChatMessage] = None) -> str:
        """Process a chat message and return the agent's response."""
        if chat_history is None:
            chat_history = []

        # Get response with chat history
        response = await self.agent.achat(message, chat_history=chat_history)
        return str(response)