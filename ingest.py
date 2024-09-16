import os
import nest_asyncio  # noqa: E402
nest_asyncio.apply()

from dotenv import load_dotenv
load_dotenv()

##### LLAMAPARSE #####
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_community.document_loaders import TextLoader

llamaparse_api_key = os.getenv("LLAMA_CLOUD")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API")
print(llamaparse_api_key)
print(qdrant_api_key)
print(qdrant_url)

# Path to your pre-existing text file
text_file_path = "./data/hospital_file.txt"

# Create vector database
def create_vector_database():
    """
    Creates a vector database using document loaders and embeddings.

    This function loads the provided text file,
    splits the loaded text into chunks, transforms them into embeddings using FastEmbedEmbeddings,
    and finally persists the embeddings into a Qdrant vector database.
    """
    # Load the text file using the TextLoader
    loader = TextLoader(text_file_path)
    documents = loader.load()
    
    # Split loaded documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    # Initialize Embeddings
    embeddings = FastEmbedEmbeddings()
    
    # Create and persist a Qdrant vector database from the chunked documents
    qdrant = Qdrant.from_documents(
        documents=docs,
        embedding=embeddings,
        url=qdrant_url,
        collection_name="rag",
        api_key=qdrant_api_key
    )

    print('Vector DB created successfully!')


if __name__ == "__main__":
    create_vector_database()