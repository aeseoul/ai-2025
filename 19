import streamlit as st
import openai

# 페이지 설정
st.set_page_config(page_title="국립부경대학교 도서관 챗봇", page_icon="📚")

# API 키 입력
api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")

# API 키 없으면 종료
if not api_key:
    st.warning("API Key를 입력하세요.")
    st.stop()

openai.api_key = api_key

# 국립부경대학교 도서관 규정집 내용
library_rules = """
1. 도서관 휴관일:
   - 매주 일요일 및 공휴일.

2. 학부생 책 대여 권수:
   - 최대 5권.
   - 대여 기간은 14일입니다.
"""

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "당신은 국립부경대학교 도서관 챗봇입니다. 도서관 규정에 대해 답변할 수 있습니다."}
    ]

# 이전 대화 출력
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 질문 입력
if prompt := st.chat_input("도서관 규정에 대해 질문해 주세요!"):
    # 사용자 입력 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 규정집 내용에 대한 답변 생성
    response = openai.ChatCompletion.create(
        model="gpt-4",  # 혹은 "gpt-3.5-turbo"
        messages=st.session_state.messages + [
            {"role": "system", "content": library_rules}  # 규정집 내용 제공
        ]
    )

    # GPT 응답
    assistant_reply = response.choices[0].message["content"]

    # GPT 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# 대화 초기화 버튼
if st.sidebar.button("🧹 초기화"):
    st.session_state.messages = [
        {"role": "system", "content": "당신은 국립부경대학교 도서관 챗봇입니다. 도서관 규정에 대해 답변할 수 있습니다."}
    ]
    st.experimental_rerun()  # 페이지 리로딩

