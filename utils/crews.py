# utils/crews.py
from api.registry import get_api_key, OPENAI_API_KEY
from utils.logs import LoggerSetup


logger = LoggerSetup("utils.crews").logger

def set_openapi_api_key_for_vision_tool():
    registered_openai_api_key = get_api_key("OPENAI_API_KEY")
    if registered_openai_api_key:
        logger.info("Set API key from customer registered API key.")
        return registered_openai_api_key
    else:
        logger.info("Consuming SNUCEM's property for providing vision service.")
        return OPENAI_API_KEY