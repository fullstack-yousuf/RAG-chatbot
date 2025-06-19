# logging messages to monitor execution flow.
import faiss
import numpy as np
import pickle
import os
import logging
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from config import Config
from utils.file_processor import FileProcessor

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self):
        logger.info("Initializing VectorDB...")
        self.embedder = SentenceTransformer(Config.EMBEDDING_MODEL)
        logger.info("Loaded embedding model: %s", Config.EMBEDDING_MODEL)
        
        self.processor = FileProcessor()
        self.index = None
        self.documents = []
        self.metadata = []
        self.embedding_dim = 384
        
        os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
        os.makedirs(Config.DOCUMENTS_PATH, exist_ok=True)
        logger.info("Ensured directory structure exists")
        
        if self._index_exists():
            logger.info("Existing FAISS index detected")
            self._load_index()
        else:
            logger.warning("No existing FAISS index found")

    def _index_exists(self) -> bool:
        exists = all([
            os.path.exists(f"{Config.VECTOR_DB_PATH}/index.faiss"),
            os.path.exists(f"{Config.VECTOR_DB_PATH}/metadata.pkl")
        ])
        logger.debug("Index existence check: %s", exists)
        return exists

    def _load_index(self):
        try:
            logger.info("Loading FAISS index...")
            self.index = faiss.read_index(f"{Config.VECTOR_DB_PATH}/index.faiss")
            with open(f"{Config.VECTOR_DB_PATH}/metadata.pkl", 'rb') as f:
                self.documents, self.metadata = pickle.load(f)
            logger.info("Successfully loaded index with %d documents", len(self.documents))
        except Exception as e:
            logger.error("Failed loading index: %s", str(e))
            self.index = None

    def add_documents(self) -> bool:
        logger.info("Starting document ingestion process")
        if self._index_exists() and len(self.documents) > 0:
            logger.info("Using existing index with %d documents", len(self.documents))
            return True
            
        processed = self._process_new_documents()
        if not processed:
            logger.error("No documents were processed successfully")
            return False
            
        self._create_new_index()
        return True

    def _process_new_documents(self) -> bool:
        logger.info("Processing new documents from %s", Config.DOCUMENTS_PATH)
        success_count = 0
        file_list = os.listdir(Config.DOCUMENTS_PATH)
        logger.debug("Found %d files in documents directory", len(file_list))
        
        for file_name in file_list:
            file_path = os.path.join(Config.DOCUMENTS_PATH, file_name)
            logger.debug("Processing %s", file_name)
            try:
                text = self.processor.process_file(file_path)
                if text:
                    self.documents.append(text)
                    self.metadata.append({"source": file_name})
                    success_count += 1
                    logger.debug("Added document %s (%d chars)", file_name, len(text))
            except Exception as e:
                logger.error("Failed processing %s: %s", file_name, str(e))
        
        logger.info("Processed %d/%d files successfully", success_count, len(file_list))
        return success_count > 0

    def _create_new_index(self):
        logger.info("Creating new FAISS index...")
        logger.debug("Encoding %d documents...", len(self.documents))
        embeddings = self.embedder.encode(self.documents, show_progress_bar=False)
        logger.debug("Embedding generation complete")
        
        embeddings = np.array(embeddings).astype('float32')
        if embeddings.shape[1] != self.embedding_dim:
            logger.error("Embedding dimension mismatch! Expected %d, got %d", 
                        self.embedding_dim, embeddings.shape[1])
            raise ValueError("Embedding dimension mismatch")
        
        logger.debug("Initializing FAISS index...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings)
        logger.info("FAISS index created with %d vectors", self.index.ntotal)
        
        self._save_index()

    def _save_index(self):
        try:
            logger.debug("Saving index to disk...")
            faiss.write_index(self.index, f"{Config.VECTOR_DB_PATH}/index.faiss")
            with open(f"{Config.VECTOR_DB_PATH}/metadata.pkl", 'wb') as f:
                pickle.dump((self.documents, self.metadata), f)
            logger.info("Index successfully saved to %s", Config.VECTOR_DB_PATH)
        except Exception as e:
            logger.error("Failed saving index: %s", str(e))
            raise

    # def query(self, query_text: str, k: int = 3) -> Dict:
    #     logger.info("Processing query: '%s'", query_text[:50] + ("..." if len(query_text) > 50 else ""))
    #     if not self.index:
    #         logger.error("Attempted query with uninitialized index!")
    #         raise ValueError("Index not initialized")
            
    #     try:
    #         logger.debug("Generating query embedding...")
    #         query_embed = self.embedder.encode([query_text])
    #         query_embed = np.array(query_embed).astype('float32')
            
    #         adaptive_k = min(max(len(query_text.split()) * 2, 10))
    #         logger.debug("Using adaptive k=%d for query", adaptive_k)
            
    #         distances, indices = self.index.search(query_embed, adaptive_k)
    #         logger.debug("FAISS search returned %d results", len(indices[0]))
            
    #         threshold = 0.7 - (0.1 * min(len(query_text.split()), 5))
    #         logger.debug("Using dynamic threshold=%.2f", threshold)
            
    #         results = {'documents': [], 'metadatas': []}
    #         for i, score in zip(indices[0], distances[0]):
    #             if score < threshold and i >= 0:
    #                 results['documents'].append(self.documents[i])
    #                 results['metadatas'].append(self.metadata[i])
    #                 logger.debug("Matched document %d with score %.3f", i, score)
    #                 if len(results['documents']) >= k:
    #                     break
                        
    #         logger.info("Query returned %d relevant documents", len(results['documents']))
    #         return results
            
    #     except Exception as e:
    #         logger.error("Query processing failed: %s", str(e))
    #        return {'documents': [], 'metadatas': []}


    # In retrieval.py, modify the query method:
    def query(self, query_text: str, k: int = 3) -> Dict:
        try:
            query_embed = self.embedder.encode([query_text])
            query_embed = np.array(query_embed).astype('float32')
            
            # Ensure k is within bounds
            k = min(k, self.index.ntotal) if self.index.ntotal > 0 else 0
            
            if k == 0:
                return {'documents': [], 'metadatas': []}
                
            distances, indices = self.index.search(query_embed, k)
            
            # Fix the results processing
            results = {'documents': [], 'metadatas': []}
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx >= 0:
                    results['documents'].append(self.documents[idx])
                    results['metadatas'].append(self.metadata[idx])
                    
            return results

        except Exception as e:
            logger.error("Query processing failed: %s", str(e))
            return {'documents': [], 'metadatas': []}
        
        
# import faiss
# import numpy as np
# import pickle
# import os
# from sentence_transformers import SentenceTransformer
# from config import Config
# from utils.file_processor import FileProcessor

# class VectorDB:
#     def __init__(self):
#         self.embedder = SentenceTransformer(Config.EMBEDDING_MODEL)
#         self.processor = FileProcessor()  # Initialize the processor
#         self.index = None
#         self.documents = []
#         self.metadata = []
        
#         if os.path.exists(f"{Config.VECTOR_DB_PATH}/index.faiss"):
#             self._load_index()

#     def _load_index(self):
#         self.index = faiss.read_index(f"{Config.VECTOR_DB_PATH}/index.faiss")
#         with open(f"{Config.VECTOR_DB_PATH}/metadata.pkl", 'rb') as f:
#             self.documents, self.metadata = pickle.load(f)

#     def add_documents(self):
#         documents = []
#         metadatas = []
        
#         for file_name in os.listdir(Config.DOCUMENTS_PATH):
#             file_path = os.path.join(Config.DOCUMENTS_PATH, file_name)
#             try:
#                 # Use the processor instance
#                 text = self.processor.process_file(file_path)
#                 if text:  # Only add if we got valid content
#                     documents.append(text)
#                     metadatas.append({"source": file_name})
#             except Exception as e:
#                 print(f"Skipping {file_name}: {str(e)}")
        
#         if documents:
#             self._update_index(documents, metadatas)

#     def _update_index(self, documents, metadatas):
#         embeddings = self.embedder.encode(documents)
#         embeddings = np.array(embeddings).astype('float32')
        
#         if self.index is None:
#             self.index = faiss.IndexFlatL2(embeddings.shape[1])
        
#         self.index.add(embeddings)
#         self.documents.extend(documents)
#         self.metadata.extend(metadatas)
#         self._save_index()

#     def _save_index(self):
#         os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
#         faiss.write_index(self.index, f"{Config.VECTOR_DB_PATH}/index.faiss")
#         with open(f"{Config.VECTOR_DB_PATH}/metadata.pkl", 'wb') as f:
#             pickle.dump((self.documents, self.metadata), f)
#     def query(self, query_text: str, k: int = 3) -> dict:
#         """Enhanced query method for VOP data"""
#         try:
#             # Pre-process query
#             query_clean = ' '.join([word.lower() for word in query_text.split() if len(word) > 2])
            
#             # Boost important VOP terms
#             if 'vop' in query_clean or 'virtual office platform' in query_clean:
#                 query_clean += " virtual office platform system solution"
            
#             # Generate embedding
#             query_embed = self.embedder.encode([query_clean])
#             query_embed = np.array(query_embed).astype('float32')
            
#             # Search with higher k initially
#             distances, indices = self.index.search(query_embed, k*3)
            
#             # Filter results by quality and uniqueness
#             unique_results = {}
#             for i, score in zip(indices[0], distances[0]):
#                 if score < 0.5:  # Quality threshold
#                     doc = self.documents[i]
#                     if doc not in unique_results:
#                         unique_results[doc] = self.metadata[i]
#                         if len(unique_results) >= k:
#                             break
            
#             return {
#                 'documents': list(unique_results.keys()),
#                 'metadatas': list(unique_results.values())
#             }
        
#         except Exception as e:
#             logger.error(f"Query error: {str(e)}")
#             return {'documents': [], 'metadatas': []}
#     # def query(self, query_text: str, k: int = 3) -> dict:
#     #     """Enhanced query with semantic matching"""
#     #     # Pre-process query to focus on key terms
#     #     query_terms = ' '.join([word.lower() for word in query_text.split() if len(word) > 3])
#     #     query_embed = self.embedder.encode([query_terms])
        
#     #     # Get most relevant chunks
#     #     distances, indices = self.index.search(query_embed, k*2)
        
#     #     # Remove duplicates and get top k results
#     #     unique_results = {}
#     #     for i in indices[0]:
#     #         doc = self.documents[i]
#     #         if doc not in unique_results:
#     #             unique_results[doc] = self.metadata[i]
#     #             if len(unique_results) >= k:
#     #                 break
        
#     #     return {
#     #         'documents': list(unique_results.keys()),
#     #         'metadatas': list(unique_results.values())
#     #     }