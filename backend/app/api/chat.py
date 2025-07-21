from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.react_agent import LegislationReActAgent
from llama_index.core.llms import ChatMessage, MessageRole
import logging
import json
from typing import List, Literal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@router.post("")
async def chat_with_agent(request: Request, chat_request: ChatRequest):
    """Chat with the ReActAgent about legislation."""
    try:
        # Log the request body
        body = await request.json()
        logger.info(f"Received request body: {body}")

        # Initialize the agent
        agent = LegislationReActAgent()
        logger.info("Agent initialized")

        async def generate():
            try:
                # Get the last message from the conversation
                last_message = chat_request.messages[-1].content
                logger.info(f"Processing message: {last_message}")

                # Convert previous messages to ChatMessage format
                chat_history = []
                for msg in chat_request.messages[:-1]:
                    role = MessageRole.USER if msg.role == "user" else MessageRole.ASSISTANT
                    chat_history.append(ChatMessage(role=role, content=msg.content))
                logger.info(f"Chat history: {chat_history}")

                # Get response with chat history
                response = await agent.chat(last_message, chat_history)
                logger.info("Generated response")

                # Format response in Vercel AI SDK format
                yield f"0: {json.dumps(response)}\n"
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                yield f"0: {json.dumps(f"I apologize, but I encountered an error: {str(e)}")}\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except Exception as e:
        logger.error(f"Error in chat_with_agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))