import logging
from flask import Flask
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, KeywordIndexParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from flasgger import Swagger
import os
from dotenv import load_dotenv
from flask_cors import CORS




# Retrieve values from environment variables


# ── LOGGER SETUP ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


load_dotenv()
logger.info("Loading environment variables...")

qdrant_url = os.getenv("QADRANT_URL")
qdrant_api_key = os.getenv("QADRANT_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")
collection_name = os.getenv("COLLECTION_NAME")
mongodb_uri = os.getenv("MONGODB_URI")

# ── QDRANT & VECTOR STORE (package‐level) ────────────────────
logger.info("Initializing Qdrant client...")
qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
)

logger.info("Creating payload index for Qdrant...")
qdrant_client.create_payload_index(
    collection_name=collection_name,
    field_name="metadata.anime_type",
    field_schema=KeywordIndexParams(
        type=models.KeywordIndexType.KEYWORD,
        is_tenant=False,
        on_disk=False,
    ),
)

logger.info("Initializing HuggingFace embeddings...")
_embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model,
)

logger.info("Building Qdrant vector store...")
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="anime_ver1",
    embedding=_embeddings,
)

logger.info("Connecting to MongoDB...")
mongo_client = MongoClient(mongodb_uri)

# ── FLASK FACTORY ────────────────────────────────────────────
def create_app():
    logger.info("Creating Flask app...")
    app = Flask(__name__)

    # Enable CORS for all routes and origins
    CORS(app)
    # ── SWAGGER SETUP ─────────────────────────────────────────
    # This will serve Swagger UI at /apidocs
    app.config['SWAGGER'] = {
        'title': 'Capstone Anime API',
        'uiversion': 3
    }
    
    Swagger(app, template_file='swagger.yaml')
    # Mongo setup
    logger.info("Setting up MongoDB configuration...")
    mongo_client = MongoClient(mongodb_uri)
    app.config["MONGO_DB"] = mongo_client["capstone"]

    # also expose vector_store if you ever want direct access
    app.config["VECTOR_STORE"] = vector_store

    # register routes
    logger.info("Registering routes...")
    from .routes import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="/capstone/v1/api")

    logger.info("Flask app created successfully.")
    return app
