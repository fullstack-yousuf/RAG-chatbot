import logging
from typing import List, Tuple
from utils.retrieval import VectorDB
from utils.generation import ResponseGenerator
from config import Config
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@st.cache_resource
def initialize_components():
    """Initialize RAG components with caching"""
    try:
        logger.info("Initializing VectorDB...")
        vector_db = VectorDB()
        
        if not vector_db.add_documents():
            raise RuntimeError("Document loading failed")
        
        logger.info("Initializing Response Generator...")
        generator = ResponseGenerator()
        
        return vector_db, generator
    except Exception as e:
        logger.critical(f"Initialization failed: {str(e)}")
        st.error("System initialization failed. Check logs.")
        st.stop()

def generate_response(message: str, chat_history: List[Tuple[str, str]], vector_db: VectorDB, generator: ResponseGenerator) -> List[Tuple[str, str]]:
    """Process user query through RAG pipeline"""
    try:
        # Document Retrieval
        retrieved = vector_db.query(message)
        if not retrieved['documents']:
            logger.warning("No documents found for query")
            return chat_history + [(message, "No relevant information found")]
        
        # Prepare Context
        context = "\n\n".join(
            f"Source: {meta['source']}\nContent: {text[:2000]}{'...' if len(text)>2000 else ''}"
            for text, meta in zip(retrieved['documents'], retrieved['metadatas'])
        )
        logger.debug(f"Context prepared for query: {message[:50]}...")
        
        # Generate Response
        response = generator.generate(message, context)
        return chat_history + [(message, str(response))]
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return chat_history + [(message, "Error processing request")]

def main():
    st.set_page_config(
        page_title="IQRA University FYP - Virtual Office Platform",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Virtual Office Platform")
    
    # Initialize components
    vector_db, generator = initialize_components()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display response
        with st.chat_message("assistant"):
            try:
                # Convert message format for processing
                tuple_history = [(m["content"], "") for m in st.session_state.messages if m["role"] == "user"]
                
                # Get response
                response = generate_response(prompt, tuple_history, vector_db, generator)[-1][1]
                
                st.markdown(response)
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                logger.error(f"UI rendering error: {str(e)}")
                st.error("Error displaying response")

if __name__ == "__main__":
    main()

# this above is a code for stream lit


# # logging messages to monitor execution flow.

# import logging
# from typing import List, Dict, Tuple
# import gradio as gr
# from utils.retrieval import VectorDB
# from utils.generation import ResponseGenerator
# from config import Config

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('app.log'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# def initialize_components() -> Tuple[VectorDB, ResponseGenerator]:
#     """Initialize with detailed logging"""
#     logger.info("="*50)
#     logger.info("Initializing RAG System")
#     logger.info("="*50)
    
#     try:
#         logger.info(">>> Initializing VectorDB...")
#         vector_db = VectorDB()
        
#         logger.info(">>> Loading documents...")
#         if not vector_db.add_documents():
#             raise RuntimeError("Document loading failed")
#         logger.info("✓ Documents loaded successfully")
        
#         logger.info(">>> Initializing Gemini...")
#         generator = ResponseGenerator()
#         logger.info("✓ Components initialized successfully")
        
#         return vector_db, generator
        
#     except Exception as e:
#         logger.critical("Initialization failed: %s", str(e))
#         raise

# # Initialize system components
# vector_db, generator = initialize_components()

# # def respond(message: str, chat_history: List[Dict]) -> List[Dict]:
# #     """Full conversation handling with tracing"""
# #     logger.info("\n" + "▄"*50)
# #     logger.info(f"NEW QUERY: {message[:100]}{'...' if len(message)>100 else ''}")
    
# #     try:
# #         # Document Retrieval Phase
# #         logger.info("PHASE 1: Document Retrieval")
# #         retrieved = vector_db.query(message)
# #         logger.info("Retrieved %d relevant chunks", len(retrieved['documents']))
        
# #         if not retrieved['documents']:
# #             logger.warning("No relevant documents found!")
# #             return chat_history + [{"role": "assistant", "content": "No relevant information found."}]
        
# #         # Context Preparation
# #         context = "\n\n".join(
# #             f"📄 {meta['source']}:\n{text[:2000]}{'...' if len(text)>2000 else ''}"
# #             for text, meta in zip(retrieved['documents'], retrieved['metadatas'])
# #         )
# #         logger.debug("Context prepared:\n%.300s...", context)
        
# #         # Response Generation
# #         logger.info("PHASE 2: Response Generation")
# #         bot_response = generator.generate(message, context)
# #         logger.info("Response generated successfully")
        
# #         # History Update
# #         new_history = chat_history + [
# #             {"role": "user", "content": message},
# #             {"role": "assistant", "content": bot_response}
# #         ]
# #         logger.info("Conversation history updated")
        
# #         return new_history
        
# #     except Exception as e:
# #         logger.error("Processing error: %s", str(e))
# # #         return chat_history + [{"role": "assistant", "content": "System error occurred. Please try again."}]

# # old responsecode////////////////////
# # def respond(message: str, chat_history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
# #     try:
# #         retrieved = vector_db.query(message)
# #         if not retrieved['documents']:
# #             return chat_history + [(message, "No relevant info found")]  # Must be tuple!
        
# #         context = "\n".join(retrieved['documents'])
# #         response = generator.generate(message, context)
# #         return chat_history + [(message, response)]  # Must be tuple!
# #     except Exception as e:
# #         logger.error(f"Error: {str(e)}")
# #         return chat_history + [(message, "Error processing request")]  # Must be tuple!
# # update response code///////////////
# # def respond(message: str, chat_history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
# #     """Process user message and return tuple-formatted responses"""
# #     try:
# #         # Document Retrieval
# #         retrieved = vector_db.query(message)
# #         if not retrieved['documents']:
# #             return chat_history + [(message, "No relevant information found")]

# #         # Response Generation
# #         context = "\n".join(retrieved['documents'])
# #         response = generator.generate(message, context)
# #         return chat_history + [(message, response)]
        
# #     except Exception as e:
# #         logger.error(f"Error: {str(e)}")
# #         return chat_history + [(message, "Error processing request")]
# # /////////////////////mix format///////////////////////////
# def respond(message: str, chat_history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
#     """Process user message and return tuple-formatted responses"""
#     try:
#         # Document Retrieval
#         retrieved = vector_db.query(message)
#         if not retrieved['documents']:
#             return chat_history + [(message, "No relevant information found")]

#         # Response Generation
#         context = "\n".join(retrieved['documents'])
#         response = generator.generate(message, context)
#         return chat_history + [(message, str(response))]  # Ensure response is string
        
#     except Exception as e:
#         logger.error(f"Error: {str(e)}")
#         return chat_history + [(message, "Error processing request")]

# def create_interface():
#     """Gradio interface with monitoring"""
#     logger.info("Building Gradio interface...")
    
#     with gr.Blocks(title="RAG Chatbot", theme=gr.themes.Soft()) as demo:
#         # Header
#         gr.Markdown("## IQRA University FYP 📚 Virtual Office Platform")
        
#         # Chatbot
#         chatbot = gr.Chatbot(
           
#             height=500,
#             avatar_images=(
#                 "https://i.imgur.com/hCYImbX.png",  # User
#                 "https://i.imgur.com/rdZV3Rj.png"   # Bot
#             ),
#             show_label=False,
#             # type="messages"
#             type="tuples"
#         )

        
#         # Controls
#         with gr.Row():
#             msg = gr.Textbox(placeholder="Ask about your documents...", scale=7)
#             submit_btn = gr.Button("Submit", variant="primary")
        
#         # Examples
#         examples = gr.Examples(
#             examples=["What is VOP?", "Summarize key points", "List important details"],
#             inputs=[msg],
#             label="Example Questions"
#         )
        
#         # Event handlers
#         msg.submit(
#             lambda m,h: ("", h + [{"role": "user", "content": m}]), 
#             [msg, chatbot], [msg, chatbot]
#         ).then(respond, [msg, chatbot], [chatbot])
        
#         submit_btn.click(
#             lambda m,h: ("", h + [{"role": "user", "content": m}]), 
#             [msg, chatbot], [msg, chatbot]
#         ).then(respond, [msg, chatbot], [chatbot])
        
#         logger.info("Interface built successfully")
#         return demo
# # /////////////////////mix format end///////////////////////////
# # /////////////////////messages format ///////////////////////////

# # /////////////////////message format end///////////////////////////
# # /////////////////////tuples format ///////////////////////////

# # /////////////////////tuples format end///////////////////////////
    

    
# if __name__ == "__main__":
#     try:
#         demo = create_interface()
#         logger.info("Launching application...")
#         demo.launch(
#             server_name="0.0.0.0",
#             server_port=7860,
#             share=False
#         )
#     except Exception as e:
#         logger.critical("Application failed: %s", str(e))
#         raise
