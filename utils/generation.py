import google.generativeai as genai
import time
import logging
from typing import Optional
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Handles response generation using Gemini AI with RAG integration"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        """
        Initialize the response generator
        
        Args:
            api_key: Gemini API key
            model: Name of the Gemini model to use
        """
        logger.info("Initializing Gemini response generator...")
        try:
            # Configure Gemini with API key
            genai.configure(api_key=api_key)
            
            # Initialize model with safety settings
            self.model = genai.GenerativeModel(
                model_name=model,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                },
                generation_config={
                    "max_output_tokens": 1000,
                    "temperature": 0.7
                }
            )
            logger.info("Successfully connected to %s", model)
        except Exception as e:
            logger.critical("Failed to initialize Gemini: %s", str(e))
            raise RuntimeError("Gemini initialization failed") from e

        # System instructions for RAG behavior
        self.system_instruction = """You are a precise RAG assistant. Follow these rules:
1. Answer STRICTLY using the provided context
2. Never invent or hallucinate information
3. If answer isn't in context, say "Not found in documents"
4. Keep responses concise (50-100 words)
5. Format responses with bullet points when appropriate"""

    def generate(self, query: str, context: str, max_retries: int = 3) -> str:
        """
        Generate a response using RAG context
        
        Args:
            query: User's question
            context: Retrieved documents context
            max_retries: Number of retry attempts
            
        Returns:
            Generated response or error message
        """
        logger.info("Generating response for query: %s", self._truncate_text(query))
        logger.debug("Context size: %d chars", len(context))
        
        prompt = self._build_prompt(query, context)
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                # Generate response with error handling
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    logger.warning("Empty response (attempt %d)", attempt + 1)
                    continue
                
                # Validate and format response
                validated = self._validate_response(response.text, query)
                elapsed = time.time() - start_time
                
                logger.info("Generated response in %.2fs", elapsed)
                logger.debug("Final response: %s", self._truncate_text(validated))
                
                return validated
                
            except Exception as e:
                logger.error("Attempt %d failed: %s", attempt + 1, str(e))
                if attempt == max_retries - 1:
                    logger.error("All retries exhausted")
                    return "⚠️ System error: Please try again later"
                
                # Exponential backoff
                time.sleep(min(2 ** attempt, 5))  # Max 5 second delay
        
        return "🚧 Temporarily unavailable. Please retry."

    def _build_prompt(self, query: str, context: str) -> str:
        """Construct the RAG prompt template"""
        return f"""SYSTEM INSTRUCTIONS:
{self.system_instruction}

CONTEXT DOCUMENTS:
{context}

USER QUESTION:
{query}

YOUR RESPONSE (STRICTLY based on context):"""

    def _validate_response(self, text: str, query: str) -> str:
        """Clean and validate the generated response"""
        # Remove common hallucinations
        replacements = [
            ("as an AI", ""),
            ("I don't have personal opinions", "The documents don't specify"),
            ("my knowledge cutoff", "the available documents"),
            ("in general", "specifically"),
            ("typically", "in this case")
        ]
        
        for phrase, replacement in replacements:
            if phrase.lower() in text.lower():
                logger.warning("Corrected phrase: %s", phrase)
                text = text.replace(phrase, replacement)
        
        # Ensure response stays on topic
        if not any(word in text.lower() for word in query.lower().split()[:3]):
            logger.warning("Possible off-topic response")
            text = "Not found in documents. Please rephrase your question."
        
        return text.strip()[:1500]  # Hard length limit

    def _truncate_text(self, text: str, length: int = 100) -> str:
        """Helper for logging long texts"""
        return text[:length] + ("..." if len(text) > length else "")


# Example usage pattern:
if __name__ == "__main__":
    try:
        # Initialize with config
        generator = ResponseGenerator(
            api_key=Config().GEMINI_API_KEY,
            model=Config().GEMINI_MODEL
        )
        
        # Test generation
        test_query = "What is VOP?"
        test_context = "VOP (Virtual Office Platform) is a digital workspace solution..."
        
        response = generator.generate(test_query, test_context)
        print("Generated response:", response)
        
    except Exception as e:
        logger.critical("Test failed: %s", str(e))

# the above is the streamlit code

# # logging messages to monitor execution flow.

# import google.generativeai as genai
# import time
# import logging
# from typing import Optional
# from config import Config

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('generation.log'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# class ResponseGenerator:
#     def __init__(self):
#         logger.info("Initializing Gemini response generator...")
#         try:
#             genai.configure(api_key=Config.GEMINI_API_KEY)
#             self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
#             logger.info("Successfully connected to %s", Config.GEMINI_MODEL)
#         except Exception as e:
#             logger.error("Failed to initialize Gemini: %s", str(e))
#             raise

#         self.system_instruction = """You are a precise RAG assistant. Follow these rules:
#         1. Answer ONLY using provided context
#         2. Never invent information
#         3. If unsure, say "Not found in documents"
#         4. Keep responses under 100 words"""
        
#         logger.debug("System instructions set")

#     def _log_generation(self, query: str, context: str):
#         logger.info("Generating response for query: %s", query[:50] + ("..." if len(query) > 50 else ""))
#         logger.debug("Context preview:\n%.100s...", context)
#         logger.debug("Context size: %d chars", len(context))

#     def generate(self, query: str, context: str, max_retries: int = Config.MAX_RETRIES) -> str:
#         self._log_generation(query, context)
        
#         prompt = f"""SYSTEM: {self.system_instruction}
        
#         CONTEXT:
#         {context}
        
#         QUESTION: {query}
        
#         ANSWER:"""
        
#         for attempt in range(max_retries):
#             try:
#                 start_time = time.time()
#                 response = self.model.generate_content(prompt)
#                 elapsed = time.time() - start_time
                
#                 if not response.text:
#                     logger.warning("Empty response (attempt %d)", attempt + 1)
#                     continue
                    
#                 logger.info("Generated response in %.2fs", elapsed)
#                 logger.debug("Raw response: %.100s...", response.text)
                
#                 validated = self._validate_response(response.text, query)
#                 logger.debug("Validated response: %.100s...", validated)
                
#                 return validated
                
#             except Exception as e:
#                 logger.error("Attempt %d failed: %s", attempt + 1, str(e))
#                 if attempt == max_retries - 1:
#                     logger.error("All retries exhausted")
#                     return "System error: Please try again later"
#                 time.sleep(Config.RETRY_DELAY * (attempt + 1))
        
#         return "Temporarily unavailable. Please retry."

#     def _validate_response(self, text: str, query: str) -> str:
#         validation_rules = [
#             ("VOP", "Virtual Office Platform"),
#             ("according to my knowledge", "Not found in documents"),
#             ("I believe", "The documents indicate"),
#             ("typically", "Specifically")
#         ]
        
#         for trigger, replacement in validation_rules:
#             if trigger.lower() in text.lower():
#                 logger.warning("Corrected hallucination trigger: %s", trigger)
#                 text = text.replace(trigger, replacement)
        
#         if "?" in text and "Not found" not in text:
#             logger.warning("Possible incomplete answer: %s", text[:50])
            
#         return text[:1000]  # Safety limit


# import google.generativeai as genai
# from config import Config
# import time
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# genai.configure(api_key=Config.GEMINI_API_KEY)

# class ResponseGenerator:
#     def __init__(self):
#         self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
#         self.system_instruction = """You are a helpful AI assistant that answers questions based on provided context.
#         Rules:
#         1. Be concise and accurate
#         2. If the answer isn't in the context, say "I don't have that information"
#         3. Never make up information"""

#     def generate(self, query: str, context: str) -> str:
#         prompt = f"""You are a Virtual Office Platform (VOP) assistant. Answer questions using ONLY the provided context.

#     CONTEXT:
#     {context}

#     QUESTION: {query}

#     INSTRUCTIONS:
#     1. For "what is VOP" questions, provide the full definition
#     2. For client queries, list: Name, Company, Project, Status
#     3. For employee queries, list: Name, Role, Department
#     4. If information is missing, say "Not found in current VOP documents"

#     ANSWER:"""
        
#         try:
#             response = self.model.generate_content(prompt)
#             return response.text if response.text else "Information not available in VOP documents"
#         except Exception as e:
#             logger.error(f"Generation error: {str(e)}")
#             return "Failed to retrieve VOP information"
#     # def generate(self, query: str, context: str, max_retries: int = Config.MAX_RETRIES) -> str:
#     #     """Generate response using Gemini model"""
#     #     full_prompt = f"""System Instruction: {self.system_instruction}
        
#     #     Context:
#     #     {context}
        
#     #     Question: {query}
        
#     #     Answer:"""
        
#     #     for attempt in range(max_retries):
#     #         try:
#     #             response = self.model.generate_content(full_prompt)
#     #             if response.text:
#     #                 return response.text
#     #             logger.warning(f"Empty response, attempt {attempt + 1}")
#     #             time.sleep(Config.RETRY_DELAY)
#     #         except Exception as e:
#     #             logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
#     #             if attempt == max_retries - 1:
#     #                 return "I'm experiencing technical difficulties. Please try again later."
#     #             time.sleep(Config.RETRY_DELAY * (attempt + 1))
        
#     #     return "The system is busy. Please try your question again in a moment."
# # ///////////////
# # import google.generativeai as genai
# # from config import Config
# # import time
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # genai.configure(api_key=Config.GEMINI_API_KEY)

# # class ResponseGenerator:
# #     def __init__(self):
# #         self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
# #         self.system_prompt = """You are a helpful AI assistant. Answer questions based strictly on the provided context.
# #         Rules:
# #         1. Be concise and accurate
# #         2. If the answer isn't in the context, say "I don't have that information"
# #         3. Never make up information"""

# #     def generate(self, query, context, max_retries=Config.MAX_RETRIES):
# #         prompt = {
# #             "system_instruction": self.system_prompt,
# #             "parts": [
# #                 {"text": f"Context:\n{context}"},
# #                 {"text": f"Question: {query}"},
# #                 {"text": "Answer:"}
# #             ]
# #         }
        
# #         for attempt in range(max_retries):
# #             try:
# #                 response = self.model.generate_content(prompt)
# #                 if response.text:
# #                     return response.text
# #                 logger.warning(f"Empty response, attempt {attempt + 1}")
# #                 time.sleep(Config.RETRY_DELAY)
# #             except Exception as e:
# #                 logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
# #                 if attempt == max_retries - 1:
# #                     return "I'm experiencing technical difficulties. Please try again later."
# #                 time.sleep(Config.RETRY_DELAY * (attempt + 1))
        
# #         return "The system is busy. Please try your question again in a moment."
# # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////
# # import google.generativeai as genai
# # from config import Config

# # genai.configure(api_key=Config.GEMINI_API_KEY)
# # model = genai.GenerativeModel('gemini-pro')

# # class ResponseGenerator:
# #     def __init__(self):
# #         self.system_prompt = """You are a helpful AI assistant. Answer questions based on the context.
# #         Rules:
# #         1. Be concise and accurate
# #         2. If unsure, say "I don't have that information"
# #         3. Never hallucinate facts"""
    
# #     def format_context(self, retrieved_data):
# #         return "\n\n".join(
# #             f"Source: {meta['source']}\nContent: {doc}"
# #             for doc, meta in zip(retrieved_data['documents'], retrieved_data['metadatas'])
# #         )

# #     def generate(self, query, context):
# #         prompt = f"""
# #         {self.system_prompt}
        
# #         Context:
# #         {context}
        
# #         Question: {query}
        
# #         Answer in 1-3 paragraphs:"""
        
# #         response = model.generate_content(prompt)
# #         return response.text