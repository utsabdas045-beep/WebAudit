import logging
import os
from pathlib import Path
from core.config import LOG_DIR


def get_logger(name: str) -> logging.Logger:
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(os.path.join(LOG_DIR, "webaudit.log"))
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
