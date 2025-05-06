import logging
from flask import Flask
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, KeywordIndexParams
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from flasgger import Swagger

# ── LOGGER SETUP ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── QDRANT & VECTOR STORE (package‐level) ────────────────────
logger.info("Initializing Qdrant client...")
qdrant_client = QdrantClient(
    url="https://00417665-6cbf-46cc-b17a-2e5771f88ac7.us-east4-0.gcp.cloud.qdrant.io",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.6MlJFRgeyQdVZYZlgmDUCURBT6ahRHjkZyFGsdicNmE"
)

logger.info("Creating payload index for Qdrant...")
qdrant_client.create_payload_index(
    collection_name="anime_ver1",
    field_name="metadata.anime_type",
    field_schema=KeywordIndexParams(
        type=models.KeywordIndexType.KEYWORD,
        is_tenant=False,
        on_disk=False,
    ),
)

logger.info("Initializing HuggingFace embeddings...")
_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

logger.info("Building Qdrant vector store...")
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="anime_ver1",
    embedding=_embeddings,
)

logger.info("Connecting to MongoDB...")
mongo_client = MongoClient("mongodb+srv://dev:dev@cluster0.hwutjuq.mongodb.net/?retryWrites=true&w=majority")

# ── FLASK FACTORY ────────────────────────────────────────────
def create_app():
    logger.info("Creating Flask app...")
    app = Flask(__name__)

    # ── SWAGGER SETUP ─────────────────────────────────────────
    # This will serve Swagger UI at /apidocs
    app.config['SWAGGER'] = {
        'title': 'Capstone Anime API',
        'uiversion': 3
    }
    Swagger(app, template_file='swagger.yaml')
    # Mongo setup
    logger.info("Setting up MongoDB configuration...")
    mongo_client = MongoClient("mongodb+srv://dev:dev@cluster0.hwutjuq.mongodb.net/?retryWrites=true&w=majority")
    app.config["MONGO_DB"] = mongo_client["capstone"]

    # also expose vector_store if you ever want direct access
    app.config["VECTOR_STORE"] = vector_store

    # register routes
    logger.info("Registering routes...")
    from .routes import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="/capstone/v1/api")

    logger.info("Flask app created successfully.")
    return app
