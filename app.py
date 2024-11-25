# app.py
import master


import os

import json
import streamlit as st

from api.registry import get_api_key
from api.models import get_model, COMMERCIAL_MODELS
from crews.crew import run_crew
from utils.logs import LoggerSetup
from utils.components import (page_config, 
                              login, 
                              image_handler, 
                              task_handler, 
                              select_model)
from utils.functions import get_args, extract_caption, transform_to_json_format_debug_fixed, json_to_md_table, json_to_html_table, get_tasks_into_chart


# Set logger
logger = LoggerSetup("app").logger

# Main Page
page_config("위험성평가 자동 생성 LLM")

# Login
login()

# Sidebar: Model Selection
st.sidebar.subheader("모델 선택")
model_options = get_args(**COMMERCIAL_MODELS)
selected_model = st.sidebar.selectbox("모델을 선택하세요:", model_options, help="Notice: 성능이 상대적으로 좋지 않은 모델은 렌더링 오류를 유발할 수 있습니다.")

# Retrieve the API key
api_key = get_api_key(model_name=selected_model)
select_model(select_model=selected_model)

# Sidebar: Task Input
st.sidebar.subheader("작업 입력")
image_path = image_handler("이미지를 업로드하세요:")
task = task_handler("작업을 입력하세요:", "공종: 빔 거푸집 설치 작업, 공정: 자재 인양")

# 위험성 평가 실행 버튼
if st.sidebar.button("위험성 평가표 작성하기"):
    logger.debug(f"Running in progress. Task: {task}")
    with st.spinner("위험성 평가표를 생성 중, 잠시만 기다려주세요. (예상 소요 시간: 1~3분)"):
        # Run crews
        try:
            result = run_crew(get_model(selected_model, api_key=api_key), image_path, task)
        except Exception as e:
            st.error(f"작업 처리 중 오류 발생: {e}")
            logger.error(f"Error: {e}")
            st.stop()
        
        # 결과 처리
        try:
            st.markdown(f"### [평가대상작업] {get_tasks_into_chart(task)}")
            json_format_output = transform_to_json_format_debug_fixed(result.raw)
            table = json_to_html_table(json_format_output)
            st.html(table)
        except Exception as e:
            st.error("결과 형식이 올바르지 않습니다.")
            logger.error(e)
            st.stop()

    # st.markdown(f"<details><summary><h3>펼쳐서 Agent 생각 보기 👇</h3></summary>{"\n".join(result.tasks_output)}</details>", unsafe_allow_html=True)
    st.markdown("### 펼쳐서 Agent 생각 보기 👇")
    st.json(result.tasks_output, expanded=False)
    st.markdown("### 펼쳐서 Raw 데이터 보기 👇")
    st.write(result, expanded=False)
    st.success("위험성 평가표 작성이 완료되었습니다.")
