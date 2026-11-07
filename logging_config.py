import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "events.log"


def log_event(level: int, message: str, *args, exc_info: bool = False) -> None:
    logger = logging.getLogger("lead_intake.events")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    # Handle each record directly, avoiding shared handlers between requests.
    try:
        record = logger.makeRecord(logger.name, level, "", 0, message, args, None)
        if exc_info:
            import sys
            record.exc_info = sys.exc_info()
        handler.handle(record)
    finally:
        handler.close()
