# utils/crews.py
from api.registry import get_api_key, OPENAI_API_KEY


def set_openapi_api_key_for_vision_tool():
    registered_openai_api_key = get_api_key("OPENAI_API_KEY")
    if registered_openai_api_key:
        return registered_openai_api_key
    else:
        return OPENAI_API_KEY