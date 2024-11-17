# api/models.py
from functools import wraps

import streamlit as st
from crewai import LLM


COMMERCIAL_MODELS = {
    "opensource": [
        "기본 모델"
    ],
    "OpenAI": [
        "gpt-4o",
        "gpt-4o-mini",
    ],
    "Anthropic": [
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
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


def get_model(model: str, **kwargs) -> object:
    """
    Get the mode object named with a given model.

    Args:
        model (str): The name of the model to look up.

    Returns:
        str: The instance of the LLM model.

    Raises:
        NotImplementedError: If the model does not implemented yet.
    """
    if get_company_name(model) == "opensource":
        raise NotImplementedError(f"{get_company_name(model)} is not supported. (Current model: {model})")
    if get_company_name(model) in COMMERCIAL_MODELS.keys():
        if "api_key" in kwargs.keys():
            return LLM(model=model, api_key=kwargs.get("api_key"))
        return LLM(model=model)
    else:
        raise NotImplementedError(f"{get_company_name(model)} is not supported. (Current model: {model})")
