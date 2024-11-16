# app.py
import json
import streamlit as st

from api.registry import get_api_key
from api.models import get_model
from crews import assemble
# from crews.processor import initialize_crew, run_crew
from utils.logs import LoggerSetup
from utils.components import select_model, COMMERCIAL_MODELS
from utils.functions import get_args, get_image_path, extract_caption, parse2chart


logger = LoggerSetup("app").logger

# Sidebar: Model Selection
st.sidebar.title("모델 선택")
model_options = get_args(**COMMERCIAL_MODELS)
selected_model = st.sidebar.selectbox("모델을 선택하세요:", model_options)
select_model(select_model=selected_model)

# Retrieve and display the API key
api_key = get_api_key(model_name=selected_model)

# Sidebar: Image Input
st.sidebar.title("작업 입력")
image_file = st.sidebar.file_uploader("이미지를 업로드하세요:", type=["jpg", "jpeg", "png"])
placeholder_value = "빔 거푸집 설치 작업"
task = st.sidebar.text_input("작업을 입력하세요:", placeholder=placeholder_value)

# Main Page
st.title("위험성평가 자동 생성 LLM")
image_placeholder = st.empty()

if image_file:
    image_path = get_image_path(image_file)  # 업로드된 파일을 임시 경로에 저장
else:
    st.error("이미지를 업로드하세요.")
    st.stop()

# 위험성 평가 실행 버튼
if st.sidebar.button("위험성 평가표 작성하기"):
    if not task:
        task = placeholder_value

    logger.debug(f"작업 실행 시작: {task}")

    with st.spinner("위험성 평가표를 생성 중, 잠시만 기다려주세요..."):
        try:
            # crews.main의 초기화 및 실행 함수 호출
            # crew = initialize_crew(get_model(selected_model))
            # result = run_crew(crew, image_path, task)
            result = assemble.run(get_model(selected_model), image_path, task)
        except Exception as e:
            st.error(f"작업 처리 중 오류 발생: {e}")
            logger.error(f"Error: {e}")
            st.stop()

        # 결과 처리
        if isinstance(result, (dict, list)):
            st.markdown(parse2chart(json.dumps(result, ensure_ascii=False)))
        else:
            st.error("결과 형식이 올바르지 않습니다.")
            logger.error(f"Invalid result format: {result}")

    st.success("위험성 평가표 작성이 완료되었습니다!")
