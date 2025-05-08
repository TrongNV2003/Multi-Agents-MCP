import json
from loguru import logger

def setup_logger():
    logger.remove()
    logger.add("logs/app.log", rotation="500 MB")
    return logger

def safe_json_parse(data: str) -> dict:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON: {data}")
        return {}