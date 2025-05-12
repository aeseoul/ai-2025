import streamlit as st
import openai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Python 3.12 대응 GPT-4.1-mini 챗봇 앱", layout="wide")

st.title("Python 3.12 대응 GPT-4.1-mini 챗봇 앱")

# 사이드바 메뉴 및 API Key 입력
page = st.sidebar.radio(
    "메뉴 선택",
    ("GPT-4.1-mini Q&A", "Chat", "도서관 챗봇", "ChatPDF")
)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.sidebar.text_input("OpenAI API Key 입력", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

if not api_key:
    st.warning("OpenAI API Key를 입력해주세요.")
    st.stop()

openai.api_key = api_key

# 부경대 도서관 규정 문자열 예시
library_rules = """
국립부경대학교 도서관 규정:
- 휴관일: 매주 일요일 및 공휴일
- 학부생 대여 권수: 최대 5권
- 반납 기한은 14일 이내
...
"""

# Chat용 메시지 세션 상태
if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []

# ChatPDF용 PDF 내용 및 질문 기록
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "chat_history_pdf" not in st.session_state:
    st.session_state.chat_history_pdf = []

if page == "GPT-4.1-mini Q&A":
    st.header("GPT-4.1-mini 질문/응답")
    prompt = st.text_input("질문을 입력하세요:", key="qa_input")
    if prompt:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()
            st.markdown(f"**응답:** {answer}")
        except Exception as e:
            st.error(f"오류 발생: {e}")

elif page == "Chat":
    st.header("Chat 페이지")
    if st.button("Clear 채팅 내용"):
        st.session_state.messages_chat = []

    user_input = st.text_input("메시지를 입력하세요:", key="chat_input")
    if user_input:
        st.session_state.messages_chat.append({"role": "user", "content": user_input})
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1-mini",
                messages=st.session_state.messages_chat,
                max_tokens=500,
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"오류 발생: {e}"
        st.session_state.messages_chat.append({"role": "assistant", "content": reply})

    for msg in st.session_state.messages_chat:
        if msg["role"] == "user":
            st.markdown(f"**사용자**: {msg['content']}")
        else:
            st.markdown(f"**챗봇**: {msg['content']}")

elif page == "도서관 챗봇":
    st.header("국립부경대학교 도서관 챗봇")
    question = st.text_input("질문을 입력하세요:", key="library_input")
    if question:
        messages = [
            {"role": "system", "content": "당신은 친절한 도서관 안내 챗봇입니다. 다음 규정을 기준으로 질문에 답해주세요."},
            {"role": "system", "content": library_rules},
            {"role": "user", "content": question},
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1-mini",
                messages=messages,
                max_tokens=500,
                temperature=0,
            )
            answer = response.choices[0].message.content.strip()
            st.markdown(answer)
        except Exception as e:
            st.error(f"오류 발생: {e}")

elif page == "ChatPDF":
    st.header("ChatPDF 페이지 - PDF 텍스트 기반 질의응답")

    uploaded_file = st.file_uploader("PDF 파일 업로드", type=['pdf'])

    if st.button("Clear PDF 데이터"):
        st.session_state.pdf_text = ""
        st.session_state.chat_history_pdf = []
        st.success("PDF 데이터 및 대화 내역 초기화됨")

    if uploaded_file:
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page_obj in pdf_reader.pages:
                page_text = page_obj.extract_text()
                if page_text:
                    text += page_text + "\n"
            st.session_state.pdf_text = text
            st.text_area("PDF 내용 미리보기", st.session_state.pdf_text, height=300)
        except Exception as e:
            st.error(f"PDF 읽기 오류: {e}")

    if st.session_state.pdf_text:
        query = st.text_input("질문을 입력하세요:", key="pdf_chat_input")
        if query:
            messages = [
                {"role": "system", "content": "아래 텍스트를 참조해서 질문에 답해주세요."},
                {"role": "system", "content": st.session_state.pdf_text},
                {"role": "user", "content": query},
            ]
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    max_tokens=500,
                    temperature=0,
                )
                answer = response.choices[0].message.content.strip()
                st.markdown(f"**답변:** {answer}")
            except Exception as e:
                st.error(f"오류 발생: {e}")
