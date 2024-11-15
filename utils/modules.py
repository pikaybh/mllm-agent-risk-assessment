from typing import Any, List

import streamlit as st

from utils.models import COMMERCIAL_MODELS



def get_args(**kwargs) -> List[Any]:
    return [item for sublist in kwargs.values() for item in sublist]


def get_company_name(model_name):
    for company, models in COMMERCIAL_MODELS.items():
        if model_name in models:
            return company
    raise ValueError(f"No model name {model_name} exists.")


def select_model(select_model: str):
    # 선택한 모델이 'GPT 모델'이면 API 키 입력란 표시
    if selected_model in get_args(**COMMERCIAL_MODELS):
        api_key = st.sidebar.text_input(f"{get_company_name(selected_model)} API 키를 입력하세요:", type="password")
        if api_key:
            st.sidebar.success("API 키가 입력되었습니다!")
    else:
        st.sidebar.info(f"{select_model} 모델을 선택하면 API 키 입력란이 나타납니다.")