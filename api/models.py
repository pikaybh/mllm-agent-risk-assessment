# api/models.py
from functools import wraps
from typing import Callable

import streamlit as st
from langchain_openai import ChatOpenAI

from api.registry import register_api_key, get_api_key


COMMERCIAL_MODELS = {
    "opensource": [
        "기본 모델"
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "Anthropic": [
        "claude-3-5-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-sonnet-20240229",
    ],
}

def get_company_name(model_name: str) -> str:
    """
    Get the company name associated with a given model.

    Args:
        model_name (str): The name of the model to look up.

    Returns:
        str: The name of the company that provides the model.

    Raises:
        ValueError: If the model name does not exist in the `COMMERCIAL_MODELS`.
    """
    for company, models in COMMERCIAL_MODELS.items():
        if model_name in models:
            return company
    raise ValueError(f"No model name {model_name} exists.")


def get_model(model: str) -> object:
    if get_company_name(model) == "OpenAI":
        return ChatOpenAI(model=model)
