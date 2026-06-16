from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from pathlib import Path

# Global variables (that may move to .env)
db_location = "./chroma_langchain_db"
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
notes_path = "notes"

vector_store = Chroma(
    collection_name="mha_campaign",
    persist_directory=db_location,
    embedding_function=embeddings
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 7}
)

class obsidianReader():
    def __init__(self, notes_path):
        self.notes_path = notes_path
    
    @staticmethod
    def readMdFiles(base_path: Path):
        for file_path in base_path.rglob("*.md"):
            yield file_path.name, file_path.read_text(encoding="utf-8")
    
    def readCharacters(self):        
        # Get NPC data
        for file_name, content in self.readMdFiles(Path(f"{self.notes_path}/characters/")):
            document = Document(
                page_content=content, 
                metadata={'structure': 'character', 'type': 'npc', 'name': file_name})
            vector_store.add_documents(documents=[document], ids=[file_name])

        # Get Player data
        for file_name, content in self.readMdFiles(Path(f"{self.notes_path}/characters/players/")):
            document = Document(
                page_content=content, 
                metadata={'structure': 'character', 'type': 'player', 'name': file_name})
            vector_store.add_documents(documents=[document], ids=[file_name])

    def readStructures(self):
        # Get structure data
        for file_name, content in self.readMdFiles(Path(f"{self.notes_path}/structures/")):
            if content.startswith(('# Description')):
                structure_type = 'entity'
            elif content.startswith(('# Members')):
                structure_type = 'group'
            elif content.startswith(('# Location')):
                structure_type = 'space'
            else:
                raise ValueError(f"Unknown structure type for file {file_name} based on content")
            
            document = Document(
                page_content=content, 
                metadata={'structure': structure_type, 'name': file_name})
            vector_store.add_documents(documents=[document], ids=[file_name])

    def readSessions(self):
        # Get arc folders
        arc_folders = [folder.name for folder in Path(f"{self.notes_path}/").iterdir() if folder.is_dir() and folder.name.startswith("arc")]

        # Get session data for each arc
        for arc in arc_folders:
            for file_name, content in self.readMdFiles(Path(f"{self.notes_path}/{arc}/")):
                document = Document(
                    page_content=content, 
                    metadata={'structure': 'session', 'arc': arc, 'session': file_name})
                vector_store.add_documents(documents=[document], ids=[file_name])

    def readNotes(self):
        self.readCharacters()
        self.readStructures()
        self.readSessions()


obsidian = obsidianReader(notes_path)
obsidian.readNotes()
