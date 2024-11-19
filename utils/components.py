# utils/components.py
import os

import streamlit as st
from dotenv import load_dotenv

from api.registry import register_api_key, get_api_key, USER_CREDENTIALS
from api.models import COMMERCIAL_MODELS, get_company_name
from utils.functions import get_args, get_image_path, is_streamlit_running

# Load environment variables once
load_dotenv()

# Initialize API_KEY_REGISTRY in session state if not already present
if "API_KEY_REGISTRY" not in st.session_state:
    st.session_state["API_KEY_REGISTRY"] = {}

def page_config(title: str):
    st.set_page_config(
        page_title=title,
        page_icon='src/favicon/logo.svg',
        initial_sidebar_state='expanded'
    )
    st.title(title)


def image_handler(description: str):
    image_placeholder = st.empty()
    image_file = st.sidebar.file_uploader(description, type=["jpg", "jpeg", "png"])

    if image_file:
        image_path = get_image_path(image_file)  # 업로드된 파일을 임시 경로에 저장
        image_placeholder.image(image_file, caption=image_file.name, width=750)
        
        return image_path

    else:
        st.warning("현장 이미지를 입력하시면 더 정확한 분석이 가능합니다.", icon="⚠️")
        return None


def login():
    """
    Display a login form and handle user authentication.

    Returns:
        bool: True if the user is logged in, False otherwise.
    """
    st.sidebar.subheader("로그인")

    # Initialize session state for login and username
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # If the user is already logged in
    if st.session_state["logged_in"]:
        st.sidebar.success(f"'{st.session_state['username']}'님, 로그인되었습니다!")
        if st.sidebar.button("로그아웃"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
        return True

    # Display login form
    with st.sidebar.form("login_form"):
        if not st.session_state["logged_in"]:
            username = st.text_input("사용자 이름")
            password = st.text_input("비밀번호", type="password")
            submit_button = st.form_submit_button("로그인")
        else:
            st.stop()

    # Handle form submission
    if submit_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.sidebar.success(f"'{username}'님, 로그인 성공!")
            return True
        else:
            st.sidebar.error("로그인 실패. 사용자 이름 또는 비밀번호를 확인하세요.")
            st.session_state["username"] = None

    return False


def task_handler(description: str, task_placeholder: str):
    task = st.sidebar.text_input(description, placeholder=task_placeholder)
    return task if task else task_placeholder


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

        # 1. Automatically assign API key if the user is logged in
        if st.session_state.get("logged_in", False):
            # Assign API key based on the user's credentials
            username = st.session_state.get("username", "default")
            if username in USER_CREDENTIALS:
                assigned_api_key = st.secrets["api_keys"].get(env_key_name)
                if assigned_api_key:
                    st.session_state["API_KEY_REGISTRY"][env_key_name] = assigned_api_key
                    st.sidebar.success(f"API 키가 사용자 '{username}'에게 자동으로 할당되었습니다.")
                    return
            else:
                st.sidebar.warning(f"사용자 '{username}'에 대한 API 키를 찾을 수 없습니다.")
                return

        # 2. Check for the API key in environment variables
        if is_streamlit_running():
            env_api_key = os.getenv(env_key_name)
            if env_api_key:
                st.session_state["API_KEY_REGISTRY"][env_key_name] = env_api_key
                st.sidebar.success("개발자 모드에서는 API 키가 필요 없습니다.")
                return

        # 3. Check for the API key in the registry
        registered_api_key = st.session_state["API_KEY_REGISTRY"].get(env_key_name)
        if registered_api_key:
            st.sidebar.success("등록된 API 키가 사용됩니다.")
            return

        # 4. Prompt user for a new API key
        entered_api_key = st.sidebar.text_input(
            f"{company_name} API 키를 입력하세요:", value="", type="password"
        )
        if entered_api_key:
            st.session_state["API_KEY_REGISTRY"][env_key_name] = entered_api_key
            st.sidebar.success("API 키가 성공적으로 등록되었습니다.")
        else:
            st.sidebar.warning("API 키를 입력해주세요.")
        return

    # Invalid model selection
    st.sidebar.error(f"Error: '{select_model}'는 유효한 모델 이름이 아닙니다.")
