# api/registry.py
from functools import wraps

import streamlit as st

from api.models import get_company_name


USER_CREDENTIALS = st.secrets["credentials"]
OPENAI_API_KEY = st.secrets["api_keys"]["OPENAI_API_KEY"]
ANTHROPIC_API_KEY = st.secrets["api_keys"]["ANTHROPIC_API_KEY"]

def init_api_key_registry_session():
    # Initialize API_KEY_REGISTRY in session state if not already present
    if "API_KEY_REGISTRY" not in st.session_state:
        st.session_state["API_KEY_REGISTRY"] = {}


def register_api_key():
    """
    Decorator to register a model and associate an API key in the session state.

    Returns:
        Callable: The wrapped function.
    """
    def decorator(func):
        @wraps(func)  # Preserve the metadata of the original function
        def wrapper(*args, **kwargs):
            # Extract model name and API key from arguments
            api_key = kwargs.get("api_key")
            select_model = kwargs.get("select_model")

            # Register the API key in session state if provided
            if api_key and select_model:
                st.session_state["API_KEY_REGISTRY"][get_api_name_from_model_name(select_model)] = api_key

            # Proceed with the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_api_key(model_name: str) -> str:
    """
    Retrieve the API key for a specific model from the session state.

    Args:
        model_name (str): The name of the model.

    Returns:
        str: The API key associated with the model, or None if not found.
    """
    registry = st.session_state.get("API_KEY_REGISTRY", {})
    return registry.get(get_api_name_from_model_name(model_name))


def get_api_name_from_model_name(model_name: str) -> str:
    return f"{get_company_name(model_name).upper()}_API_KEY"