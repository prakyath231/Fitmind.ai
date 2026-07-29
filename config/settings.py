import os
from dotenv import load_dotenv

load_dotenv()

# LLM
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-small-latest"

# Embedding
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_DEVICE = "cpu"
EMBEDDING_DIM = 768

# Qdrant
QDRANT_PATH = "./qdrant_storage"
QDRANT_LOGS_COLLECTION = "fitmind_logs"
QDRANT_KB_COLLECTION = "fitmind_knowledge_base"

# BM25
BM25_INDEX_PATH = "./bm25_index.pkl"

# Retrieval
DENSE_TOP_K = 10
SPARSE_TOP_K = 10
FINAL_TOP_K = 5
RRF_K = 60

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 50

# User Profile
USER_NAME = "Prakyath"
USER_WEIGHT_KG = 75
USER_HEIGHT_CM = 175
USER_AGE = 24
USER_GOAL = "recomposition"
TRAINING_DAYS_PER_WEEK = 4

# Macros
PROTEIN_PER_KG = 2.0
CALORIE_SURPLUS_BULK = 300
CALORIE_DEFICIT_CUT = 400

# USDA
USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# Langfuse
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

# Progressive overload
OVERLOAD_INCREMENT_KG = 2.5
OVERLOAD_TARGET_REPS = 10

# Overtraining
MAX_SESSIONS_PER_MUSCLE_PER_WEEK = 2
REST_DAYS_REQUIRED = 2
