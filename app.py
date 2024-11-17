# app.py
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except:
    pass


import json
import streamlit as st

from api.registry import get_api_key
from api.models import get_model
# from crews import assemble
# from crews.processor import initialize_crew, run_crew
from crews.crew import run_crew
from utils.logs import LoggerSetup
from utils.components import select_model, COMMERCIAL_MODELS
from utils.functions import get_args, get_image_path, extract_caption, transform_to_json_format_debug_fixed, json_to_md_table  # parse2chart
from utils.os import fix_trouble


logger = LoggerSetup("app").logger

# fix_trouble()

TITLE = "위험성평가 자동 생성 LLM"
# Main Page
st.set_page_config(
    page_title=TITLE,
    page_icon='src/favicon/logo.svg',
    initial_sidebar_state='expanded'
)
st.title(TITLE)
image_placeholder = st.empty()

# Sidebar: Model Selection
st.sidebar.title("모델 선택")
model_options = get_args(**COMMERCIAL_MODELS)
selected_model = st.sidebar.selectbox("모델을 선택하세요:", model_options, help="Notice: 성능이 상대적으로 좋지 않은 모델은 렌더링 오류를 유발할 수 있습니다.")
select_model(select_model=selected_model)

# Retrieve and display the API key
api_key = get_api_key(model_name=selected_model)

# Sidebar: Image Input
st.sidebar.title("작업 입력")
image_file = st.sidebar.file_uploader("이미지를 업로드하세요:", type=["jpg", "jpeg", "png"])
placeholder_value = "빔 거푸집 설치 작업"
task = st.sidebar.text_input("작업을 입력하세요:", placeholder=placeholder_value)

if image_file:
    image_path = get_image_path(image_file)  # 업로드된 파일을 임시 경로에 저장
    image_placeholder.image(image_file, caption=image_file.name, use_container_width=True)
else:
    st.write("이미지를 업로드하세요.")
    st.stop()

# 위험성 평가 실행 버튼
if st.sidebar.button("위험성 평가표 작성하기"):
    if not task:
        task = placeholder_value

    logger.debug(f"작업 실행 시작: {task}")

    with st.spinner("위험성 평가표를 생성 중, 잠시만 기다려주세요..."):
        try:
            result = run_crew(get_model(selected_model, api_key=api_key), image_path, task)
            st.json(result, expanded=False)
        except Exception as e:
            st.error(f"작업 처리 중 오류 발생: {e}")
            logger.error(f"Error: {e}")
            st.stop()

        # 결과 처리
        try:
            json_format_output = transform_to_json_format_debug_fixed(result.raw)
            markdown_table = json_to_md_table(json_format_output)
            st.markdown(markdown_table, unsafe_allow_html=True)
        except Exception as e:
            st.error("결과 형식이 올바르지 않습니다.")
            logger.error(e)
            st.stop()

    st.success("위험성 평가표 작성이 완료되었습니다!")