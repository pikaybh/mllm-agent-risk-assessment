import streamlit as st

from utils.modules import select_model


# 사이드바에 모델 선택
st.sidebar.title("모델 선택")
model_options = ["기본 모델", "GPT 모델"]
selected_model = st.sidebar.selectbox("모델을 선택하세요:", model_options)


selected_model(selected_model)
"""
# 선택한 모델이 'GPT 모델'이면 API 키 입력란 표시
if selected_model == "GPT 모델":
    api_key = st.sidebar.text_input("GPT API 키를 입력하세요:", type="password")
    if api_key:
        st.sidebar.success("API 키가 입력되었습니다!")
else:
    st.sidebar.info("GPT 모델을 선택하면 API 키 입력란이 나타납니다.")
"""

# 메인 화면
st.title("모델 선택 및 API 키 입력 예제")
st.write(f"현재 선택된 모델: {selected_model}")

if selected_model == "GPT 모델":
    if api_key:
        st.write("GPT 모델이 활성화되었습니다!")
    else:
        st.warning("API 키를 입력해야 GPT 모델을 사용할 수 있습니다.")
else:
    st.write("기본 모델을 사용 중입니다.")