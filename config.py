import os
import streamlit as st
import logging
from typing import Optional
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Central configuration management for the RAG chatbot"""
    
    def __init__(self):
        """Initialize configuration with fallback values"""
        load_dotenv()  # Load .env file if exists
        
        # API Configuration
        self.GEMINI_API_KEY = self._get_secret("GEMINI_API_KEY")
        self.OPENAI_API_KEY = self._get_secret("OPENAI_API_KEY", required=False)
        
        # Model Configuration
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Path Configuration
        self.VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "knowledge_base/faiss_db")
        self.DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "knowledge_base/documents")
        
        # Performance Settings
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
        self.RETRY_DELAY = float(os.getenv("RETRY_DELAY", 1.0))
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
        
        # UI Settings
        self.PAGE_TITLE = os.getenv("PAGE_TITLE", "IQRA University - Virtual Office Platform")
        self.PAGE_ICON = os.getenv("PAGE_ICON", "📚")
        
        self._validate_config()
    
    def _get_secret(self, key: str, required: bool = True) -> Optional[str]:
        """Retrieve secret from Streamlit secrets or environment variables"""
        try:
            # Try Streamlit secrets first
            if key in st.secrets:
                logger.info(f"Loaded {key} from Streamlit secrets")
                return st.secrets[key]
            
            # Fallback to environment variables
            value = os.getenv(key)
            if value:
                logger.info(f"Loaded {key} from environment variables")
                return value
            
            if required:
                raise ValueError(f"Missing required configuration: {key}")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load {key}: {str(e)}")
            if required:
                raise
            return None
    
    def _validate_config(self):
        """Validate critical configurations"""
        if not os.path.exists(self.DOCUMENTS_PATH):
            logger.warning(f"Documents path does not exist: {self.DOCUMENTS_PATH}")
            os.makedirs(self.DOCUMENTS_PATH, exist_ok=True)
            
        if not os.path.exists(self.VECTOR_DB_PATH):
            logger.warning(f"Vector DB path does not exist: {self.VECTOR_DB_PATH}")
            os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)
        
        logger.info("Configuration validation complete")
    
    def __str__(self):
        """Safe string representation (hides sensitive keys)"""
        return (
            f"Config("
            f"model={self.GEMINI_MODEL}, "
            f"embedding={self.EMBEDDING_MODEL}, "
            f"db_path={self.VECTOR_DB_PATH}, "
            f"docs_path={self.DOCUMENTS_PATH}, "
            f"chunk_size={self.CHUNK_SIZE}, "
            f"max_retries={self.MAX_RETRIES}"
            ")"
        )

# Singleton configuration instance
try:
    config = Config()
    logger.info(f"Configuration loaded successfully: {config}")
except Exception as e:
    logger.critical(f"Failed to initialize configuration: {str(e)}")
    raise

    # this is the above code for the stremlit

# # logging messages to monitor execution flow.

# import os
# from dotenv import load_dotenv
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# logger.info("Loading configuration...")
# load_dotenv()

# class Config:
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#     if not GEMINI_API_KEY:
#         logger.error("GEMINI_API_KEY not found in .env file!")
#     else:
#         logger.info("Gemini API key loaded successfully")

#     GEMINI_MODEL = "gemini-1.5-flash"
#     VECTOR_DB_PATH = "knowledge_base/faiss_db"
#     DOCUMENTS_PATH = "knowledge_base/documents"
#     EMBEDDING_MODEL = "all-MiniLM-L6-v2"
#     MAX_RETRIES = 3
#     RETRY_DELAY = 1
    
#     logger.info(f"Configuration initialized with model {GEMINI_MODEL} and embedding {EMBEDDING_MODEL}")

# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # class Config:
# #     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# #     GEMINI_MODEL = "gemini-1.5-flash"  # Using the flash model
# #     VECTOR_DB_PATH = "knowledge_base/faiss_db"
# #     DOCUMENTS_PATH = "knowledge_base/documents"
# #     EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# #     MAX_RETRIES = 3
# #     RETRY_DELAY = 1  # seconds