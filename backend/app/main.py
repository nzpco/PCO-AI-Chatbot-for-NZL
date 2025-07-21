from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
import logging

from .db.mongodb import init_mongodb, close_mongodb_connection
from .api import legislation, tools, chat
from .observability import init_observability

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG API",
    description="API for RAG-based chatbot using LlamaIndex",
    version="0.1.0"
)

init_observability()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up MongoDB client...")
    try:
        app.mongodb_client = await init_mongodb()
        logger.info("MongoDB client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB client: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongodb_connection(app.mongodb_client)

# Include routers first
app.include_router(legislation.router)
app.include_router(tools.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}