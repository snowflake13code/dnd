# Locations
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

NOTES_LOCATION = "../mha_notes"
VEC_DB_LOCATION = "./database/chroma_langchain_db"
GRAPH_DB_LOCATION = './database/knowledge_graph'

# Vector-store related data
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

vector_store = Chroma(
    collection_name="mha_campaign",
    persist_directory=VEC_DB_LOCATION,
    embedding_function=embeddings
)


# Retriever related data
INITIAL_K = 3
FINAL_K = 5
GRAPH_DECAY = 0.9