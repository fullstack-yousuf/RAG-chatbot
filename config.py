import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self._gemini_api_key = None
        self.GEMINI_MODEL = "gemini-1.5-flash"
        self.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        self.VECTOR_DB_PATH = "knowledge_base/faiss_db"
        self.DOCUMENTS_PATH = "knowledge_base/documents"
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 1
        self._load_api_key()

    def _load_api_key(self):
        """Load API key from Streamlit secrets or environment"""
        try:
            self._gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
            if not self._gemini_api_key:
                raise ValueError("GEMINI_API_KEY not found in secrets or environment variables")
            logger.info("Successfully loaded Gemini API key")
        except Exception as e:
            logger.critical(f"Failed to load API key: {str(e)}")
            raise

    @property
    def GEMINI_API_KEY(self):
        """Get the loaded API key"""
        if not self._gemini_api_key:
            raise ValueError("API key not initialized")
        return self._gemini_api_key

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