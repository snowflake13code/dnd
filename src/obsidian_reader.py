from langchain_core.documents import Document
from pathlib import Path
from graph_db import GraphDB
import re
import json

# Get config variables
from config import NOTES_LOCATION, GRAPH_DB_LOCATION, JSON_STATE_LOCATION, vector_store

graph = GraphDB(GRAPH_DB_LOCATION)
graph.create()


class obsidianReader():
    def __init__(self, notes_path: Path, graph: GraphDB):
        self.notes_path = notes_path
        self.graph = graph

        self.latest_arc = 0
        self.latest_session = 0
    
    def saveJson(self):
        with open(JSON_STATE_LOCATION, "w") as f:
            json.dump(
                {
                    "latest_arc": self.latest_arc,
                    "latest_session": self.latest_session,
                },
                f,
                indent=4
            )

    @staticmethod
    def readMdFiles(base_path: Path):
        for file_path in base_path.rglob("*.md"):
            yield file_path.name, file_path.read_text(encoding="utf-8")

    def preProcessContent(self, name: str, content: str, path: Path, tag: str = '', header: str = None) -> str:

        if header is None:
            header = name

        # Add the name to the start of the content
        content = f"# {header}\n\n{content}"

        # Add/update the current note in the graph
        self.graph.addNode(name=name, path=str(path), tag=tag)

        # Remove all #todo tags
        content = re.sub(r"#todo\b", "", content, flags=re.IGNORECASE)

        # Handle Obsidian links
        def replace_link(match):
            link_text = match.group(1)
            target = link_text.split("|", 1)[0].strip().lower()
            self.graph.link(name, target)
            return target

        content = re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)

        return content

    def chunkSession(self, content: str, arc: str, file_path: str) -> tuple[list[Document], list[str]]:
        session_name = file_path.split(' ')[-1][:-3]    # Remove .md extension
        arc_name = arc[4:]                              # Remove the "Arc " prefix

        # Split the content into scenes
        scene_pattern = re.compile(rf"^### \s*(.*?)\:?(?:\s+#(\S+))?\s*$", re.MULTILINE)
        matches = list(scene_pattern.finditer(content))

        # Extract the scenes and create documents
        documents, ids = [], []
        for i, match in enumerate(matches):
            scene_name = match.group(1).strip()
            scene_tag = '' if match.group(2) is None else match.group(2).strip()
            scene_id = f"{arc_name}_{session_name}_{i}"

            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            scene_text = content[start:end].strip()
            scene_text = self.preProcessContent(name=scene_id, content=scene_text, path=file_path, tag=scene_tag, header=f"Arc {arc_name} - Session {session_name} - Scene {i}:")

            documents.append(Document(
                page_content=scene_text,
                metadata={
                    "id": scene_id,
                    "type": "scene",
                    "arc": arc_name,
                    "session": session_name,
                    "scene": str(i),
                    "name": scene_name,
                    "tag": scene_tag,
                    "source_file": file_path}))
            ids.append(scene_id)
        return documents, ids

    def readCharacters(self):        
        # Get NPC data
        for file_name_ext, content in self.readMdFiles(Path(f"{self.notes_path}/characters/")):
            file_name = file_name_ext[:-3].lower()
            content = self.preProcessContent(name=file_name, content=content, path=f"{self.notes_path}/characters/{file_name_ext}")
            document = Document(
                page_content=content, 
                metadata={"id": file_name, 'structure': 'character', 'type': 'npc', 'name': file_name})
            vector_store.add_documents(documents=[document], ids=[file_name])

        # Get Player data
        for file_name_ext, content in self.readMdFiles(Path(f"{self.notes_path}/characters/players/")):
            file_name = file_name_ext[:-3].lower()
            content = self.preProcessContent(name=file_name, content=content, path=f"{self.notes_path}/characters/{file_name_ext}")
            document = Document(
                page_content=content, 
                metadata={"id": file_name, 'structure': 'character', 'type': 'player', 'name': file_name})
            vector_store.add_documents(documents=[document], ids=[file_name])

    def readStructures(self):
        # Get structure data
        for file_name_ext, content in self.readMdFiles(Path(f"{self.notes_path}/structures/")):
            file_name = file_name_ext[:-3].lower()
            if content.startswith(('# Description')):
                structure_type = 'entity'
            elif content.startswith(('# Members')):
                structure_type = 'group'
            elif content.startswith(('# Location')):
                structure_type = 'space'
            else:
                raise ValueError(f"Unknown structure type for file {file_name_ext} based on content")
            
            content = self.preProcessContent(name=file_name, content=content, path=f"{self.notes_path}/structures/{file_name_ext}")
            document = Document(
                page_content=content, 
                metadata={"id": file_name, "structure": structure_type, "name": file_name})
            vector_store.add_documents(documents=[document], ids=[file_name])

    def readSessions(self):

        # Get arc folders
        arc_folders = [folder.name for folder in Path(f"{self.notes_path}/").iterdir() if folder.is_dir() and folder.name.startswith("arc")]

        # Get scene data for each arc
        for arc in arc_folders:
            for file_name, content in self.readMdFiles(Path(f"{self.notes_path}/{arc}/")):
                documents, scene_ids = self.chunkSession(content, arc, file_path=f"{self.notes_path}/{arc}/{file_name}")
                vector_store.add_documents(documents=documents, ids=scene_ids)

                # Update the latest arc and session
                SESSION_PATTERN = re.compile(r"Arc\s+(\d+)\s+Session\s+(\d+)", re.IGNORECASE)
                match = SESSION_PATTERN.match(file_name[:-3])  # remove .md
                if match:
                    arc_num = int(match.group(1))
                    session_num = int(match.group(2))

                    if (arc_num > self.latest_arc or (arc_num == self.latest_arc and session_num > self.latest_session)):
                        self.latest_arc = arc_num
                        self.latest_session = session_num

    def resolveSessionGhosts(self):
        result = self.graph.conn.execute("""
        MATCH (g:Note)
        WHERE g.ghost = true
        RETURN g.name
        """)

        SESSION_PATTERN = re.compile(r"^Arc\s+(\d+)\s+Session\s+(\d+)$", re.IGNORECASE)

        while result.has_next():
            ghost_name = result.get_next()[0]

            match = SESSION_PATTERN.match(ghost_name)
            if not match:
                continue

            arc_num = match.group(1)
            session_num = match.group(2)

            scenes = self.graph.conn.execute(f"""
            MATCH (s:Note)
            WHERE s.name STARTS WITH "{arc_num}_{session_num}_"
            RETURN s.name
            """)

            scene_names = []
            while scenes.has_next():
                scene_names.append(scenes.get_next()[0])

            if not scene_names:
                continue

            incoming = self.graph.conn.execute(f"""
            MATCH (src:Note)-[:LINKS_TO]->(g:Note {{name: "{ghost_name}"}})
            RETURN src.name
            """)

            sources = []
            while incoming.has_next():
                sources.append(incoming.get_next()[0])

            for src in sources:
                for dst in scene_names:
                    self.graph.link(src, dst)

            self.graph.conn.execute(f"""
            MATCH (g:Note {{name: "{ghost_name}"}})
            DETACH DELETE g
            """)

    def readNotes(self):
        self.readCharacters()
        self.readStructures()
        self.readSessions()
        self.resolveSessionGhosts()
        self.saveJson()


if __name__ == "__main__":
    reader = obsidianReader(NOTES_LOCATION, graph)
    reader.readNotes()