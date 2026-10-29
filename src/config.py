import os
from dotenv import load_dotenv

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Locations

NOTES_LOCATION = os.getenv("NOTES_LOCATION", "../mha_notes")
DATABASE_LOCATION = os.getenv("DATABASE_LOCATION", "./database")
VEC_DB_LOCATION = os.path.join(DATABASE_LOCATION, "chroma_langchain_db")
GRAPH_DB_LOCATION = os.path.join(DATABASE_LOCATION, "knowledge_graph")
JSON_STATE_LOCATION = os.path.join(DATABASE_LOCATION, "latest_state.json")
LOG_LOCATION = './log/code.log'

# Vector-store related data
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vector_store = Chroma(
    collection_name="mha_campaign",
    persist_directory=VEC_DB_LOCATION,
    embedding_function=embeddings
)

# Retriever related data
INITIAL_K = 5
FINAL_K = 8
GRAPH_DECAY = 0.9

# History related data
WINDOW_SIZE = 6
