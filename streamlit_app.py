import streamlit as st
import openai

st.set_page_config("GPT-4.1-mini 예제", layout="centered")

# API Key 입력 및 세션 상태 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("OpenAI API Key 입력", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

# 질문과 답변 캐시 함수
@st.cache_data(show_spinner=False)
def get_gpt_response(api_key: str, prompt: str):
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"오류 발생: {e}"

st.title("GPT-4.1-mini 질문/응답 데모")

if api_key:
    prompt = st.text_input("질문을 입력하세요:")
    if prompt:
        with st.spinner("응답 생성 중..."):
            answer = get_gpt_response(api_key, prompt)
        st.markdown(f"**응답:** {answer}")
else:
    st.warning("OpenAI API Key를 입력해주세요.")
