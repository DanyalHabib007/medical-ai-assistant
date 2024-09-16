import logging
import warnings
from qdrant_client import QdrantClient
from llama_index.llms.ollama import Ollama
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory import ChatMemoryBuffer

warnings.filterwarnings("ignore")

class AIVoiceAssistant:
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

        # Initialize Qdrant client
        self._qdrant_url = "http://localhost:6333"
        self._client = QdrantClient(url=self._qdrant_url, prefer_grpc=False)

        # Configure global settings
        Settings.llm = Ollama(model="llama3.1", request_timeout=120.0)
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        self._index = None

        # Create knowledge base and chat engine
        self._create_kb()
        self._create_chat_engine()

    def _create_chat_engine(self):
        if self._index is None:
            self._logger.error("Knowledge base creation failed. Cannot create chat engine.")
            return

        memory = ChatMemoryBuffer.from_defaults(token_limit=4500)
        self._chat_engine = self._index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=self._prompt
        )
        self._logger.info("Chat engine created successfully!")

    def _create_kb(self):
        try:
            self._logger.info("Starting to create the knowledge base...")
            reader = SimpleDirectoryReader(
                input_files=[r"C:\Users\HP\Downloads\voice_assistant_llm-main\voice_assistant_llm-main\rag\hospital_file.txt"]
            )
            documents = reader.load_data()
            vector_store = QdrantVectorStore(client=self._client, collection_name="hospital_db")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            self._index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
            )
            self._logger.info("Knowledge base created successfully!")
        except Exception as e:
            self._logger.error(f"Error while creating knowledge base: {e}")
            self._index = None  # Ensure that self._index is None if an error occurs

    def interact_with_llm(self, customer_query):
        if not hasattr(self, '_chat_engine'):
            self._logger.error("Chat engine is not initialized.")
            return None

        try:
            response = self._chat_engine.chat(customer_query)
            answer = response.response
            return answer
        except Exception as e:
            self._logger.error(f"Error during interaction with LLM: {e}")
            return None

    @property
    def _prompt(self):
        return """
            You are a voice assistant for Ranchi's Hospital, located at M G road, Ranchi, Jharkhand. The hospital operates 24/7 for emergencies, with regular outpatient services from 9 AM to 6 PM daily, except on national holidays.
            Start with greeting as 'Hello, this is Jane from Ranchi's Hospital. How can I assist you today?'
            Ranchi's Hospital provides a wide range of medical services including emergency care, general practice, and various specialist consultations.

            Your task is to gather information from the caller who wishes to schedule an appointment or inquire about services in the following manner:
            1. Ask the caller for his/her full name.
            2. Ask the caller for their contact number.
            3. Ask the caller about the reason for their call or the type of medical service they're seeking, and save it into the `appointment_details` variable.

            - Be empathetic and professional, but try to keep a light tone when appropriate.
            - Keep all your responses short and simple. Use casual language, phrases like "Umm...", "Well...", and "I mean" are preferred, but maintain a professional demeanor.
            - This is a voice conversation, so keep your responses concise, like in a real conversation. Don't provide too much information at once.
            - If the caller mentions any urgent medical conditions or emergencies, advise them to come to the emergency department immediately or call for an ambulance if necessary.
            """

