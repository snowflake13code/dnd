from pathlib import Path
import shutil
from src.obsidian_reader import obsidianReader


def reloadData():
    # Delete old logs/database directories
    directories_to_delete = ["logs", "database"]

    for directory in directories_to_delete:
        path = Path(directory)

        if path.exists():
            shutil.rmtree(path)

    # Load new data
    reader = obsidianReader()
    reader.readNotes()


if __name__ == "__main__":
    reloadData()