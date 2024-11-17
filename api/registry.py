# api/registry.py
from api.models import get_company_name


API_KEY_REGISTRY = {}

def register_api_key():
    """
    Decorator to register a model and associate an API key in the registry.

    Returns:
        Callable: The wrapped function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract model name and API key from arguments
            api_key = kwargs.get("api_key")
            select_model = kwargs.get("select_model")

            # Register the API key if provided
            if api_key and select_model:
                API_KEY_REGISTRY[select_model] = api_key

            # Proceed with the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_api_key(model_name: str) -> str:
    """
    Retrieve the API key for a specific model from the registry.

    Args:
        model_name (str): The name of the model.

    Returns:
        str: The API key associated with the model, or None if not found.
    """
    return API_KEY_REGISTRY.get(f"{get_company_name(model_name).upper()}_API_KEY")
