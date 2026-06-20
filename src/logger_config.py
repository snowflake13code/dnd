import logging
from pathlib import Path
from config import LOG_LOCATION

Path("log").mkdir(exist_ok=True)

logger = logging.getLogger("dnd")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler(LOG_LOCATION)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%H:%M:%S"))

    logger.addHandler(handler)
    logger.propagate = False