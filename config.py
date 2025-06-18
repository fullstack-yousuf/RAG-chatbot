import os
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class Config:
    # Class variables (constants)
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    GEMINI_MODEL = "gemini-pro"
    VECTOR_DB_PATH = "knowledge_base/faiss_db"
    DOCUMENTS_PATH = "knowledge_base/documents"
    
    # Instance variables (for secrets)
    def __init__(self):
        self.GEMINI_API_KEY = self._get_secret("GEMINI_API_KEY")
        
    def _get_secret(self, key: str) -> str:
        try:
            return st.secrets[key] or os.getenv(key)
        except Exception as e:
            logger.critical(f"Missing {key}: {str(e)}")
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