import os

import streamlit as st
from dotenv import load_dotenv

from api.registry import register_api_key, get_api_key, API_KEY_REGISTRY
from api.models import COMMERCIAL_MODELS, get_company_name
from utils.functions import get_args, is_streamlit_running

# Load environment variables once
load_dotenv()


@register_api_key()
def select_model(select_model: str, api_key: str = None) -> None:
    """
    Handle the selection of a model and prompt for API key input if necessary.

    Args:
        select_model (str): The name of the model selected by the user.
        api_key (str, optional): The API key to register, if provided.

    Returns:
        None
    """
    # Handle open-source models
    if select_model in COMMERCIAL_MODELS["opensource"]:
        st.sidebar.info("기본 모델은 OO를 기반으로 XX 데이터를 학습시킨 모델입니다.")
        return

    # Validate if the selected model is a commercial model
    if select_model in get_args(**COMMERCIAL_MODELS):
        try:
            company_name = get_company_name(select_model)
        except ValueError as e:
            st.sidebar.error(f"Error: {e}")
            return

        env_key_name = f"{company_name.upper()}_API_KEY"

        # 1. Check for the API key in environment variables
        if is_streamlit_running():
            env_api_key = os.getenv(env_key_name)
            if env_api_key:
                API_KEY_REGISTRY[select_model] = env_api_key
                st.sidebar.success("개발자 모드에서는 API 키가 필요 없습니다.")
                return

        # 2. Check for the API key in the registry
        registered_api_key = get_api_key(select_model)
        if registered_api_key:
            st.sidebar.success("등록된 API 키가 사용됩니다.")
            return

        # 3. Prompt user for a new API key
        entered_api_key = st.sidebar.text_input(
            f"{company_name} API 키를 입력하세요:", value="", type="password"
        )
        if entered_api_key:
            API_KEY_REGISTRY[select_model] = entered_api_key
            st.sidebar.success("API 키가 성공적으로 등록되었습니다.")
        else:
            st.sidebar.warning("API 키를 입력해주세요.")
        return

    # Invalid model selection
    st.sidebar.error(f"Error: '{select_model}'는 유효한 모델 이름이 아닙니다.")
