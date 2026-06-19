import kuzu
from pathlib import Path
import shutil


class GraphDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = kuzu.Database(self.db_path)
        self.conn = kuzu.Connection(self.db)

    def create(self) -> None:
        """
        Initialize the database and schema.
        Safe to call multiple times.
        """

        try:
            self.conn.execute("""
            CREATE NODE TABLE Note(
                name STRING,
                path STRING,
                ghost BOOL,
                tag STRING,
                PRIMARY KEY(name)
            )
            """)
        except Exception:
            pass

        try:
            self.conn.execute("""
            CREATE REL TABLE LINKS_TO(
                FROM Note TO Note
            )
            """)
        except Exception:
            pass

    def addNode(self, name: str, path: str, tag: str) -> None:
        """
        Create or update a note.
        """

        self.conn.execute(f"""
        MERGE (n:Note {{name: "{name}"}})
        SET n.path = "{path}",
            n.ghost = {"false"},
            n.tag = "{tag}"
        """)

    def ensureNode(self, name: str) -> None:
        """
        Create a ghost node only if it doesn"t exist.
        Existing nodes are left untouched.
        """

        self.conn.execute(f"""
        MERGE (n:Note {{name: "{name}"}})
        ON CREATE
            SET n.path = "",
                n.ghost = true,
                n.tag = ""
        """)

    def link(self, a: str, b: str) -> None:
        """
        Create:
            a -> b

        If either node does not exist,
        create it as a ghost node.
        """

        self.ensureNode(a)
        self.ensureNode(b)

        self.conn.execute(f"""
        MATCH (a:Note {{name: "{a}"}})
        MATCH (b:Note {{name: "{b}"}})
        MERGE (a)-[:LINKS_TO]->(b)
        """)

    def fetchConnections(self, a: str) -> list[str]:
        """
        Return all notes linked from note "a".
        """

        result = self.conn.execute(f"""
        MATCH (a:Note {{name: "{a}"}})
              -[:LINKS_TO]->
              (b:Note)
        RETURN b.name
        """)

        connections = []

        while result.has_next():
            row = result.get_next()
            connections.append(row[0])

        return connections

    def getNode(self, name: str) -> list:
        """
        Return node information as a list.
        """

        result = self.conn.execute(f"""
        MATCH (n:Note {{name: "{name}"}})
        RETURN n.name, n.path, n.ghost, n.tag
        """)

        if result.has_next():
            return result.get_next()

        return None

    def destroy(self):
        """
        Delete the graph database from disk.
        """
        db_path = Path(self.db_path)

        if db_path.exists():
            shutil.rmtree(db_path)
