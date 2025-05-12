import streamlit as st
import openai
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain

st.set_page_config(page_title="통합 GPT-4.1-mini 챗봇 앱", layout="wide")

st.title("통합 GPT-4.1-mini 챗봇 앱")

# API Key 입력 및 세션 상태 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input("OpenAI API Key 입력", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key

if not api_key:
    st.warning("OpenAI API Key를 입력해주세요.")
    st.stop()

openai.api_key = api_key

# 세션 상태 초기화
if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []

if "pdf_vectors" not in st.session_state:
    st.session_state.pdf_vectors = None

if "chat_history_pdf" not in st.session_state:
    st.session_state.chat_history_pdf = []

# 부경대 도서관 규정
library_rules = """
국립부경대학교 도서관 규정:
- 휴관일: 매주 일요일 및 공휴일
- 학부생 대여 권수: 최대 5권
- 반납 기한은 14일 이내
...
"""

tab1, tab2, tab3, tab4 = st.tabs(["GPT-4.1-mini Q&A", "Chat", "도서관 챗봇", "ChatPDF"])

# 1. GPT-4.1-mini Q&A
with tab1:
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

# 2. Chat
with tab2:
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

# 3. 도서관 챗봇
with tab3:
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

# 4. ChatPDF
with tab4:
    st.header("ChatPDF 페이지")
    uploaded_file = st.file_uploader("PDF 파일 업로드", type=['pdf'])
    if st.button("Clear PDF 데이터"):
        st.session_state.pdf_vectors = None
        st.session_state.chat_history_pdf = []
        st.success("PDF 데이터 및 대화 내역 초기화됨")

    if uploaded_file:
        if st.session_state.pdf_vectors is None:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

            text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(text)

            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            vectorstore = FAISS.from_texts(chunks, embeddings)

            st.session_state.pdf_vectors = vectorstore
            st.session_state.chat_history_pdf = []

        query = st.text_input("질문을 입력하세요:", key="pdf_chat_input")
        if query and st.session_state.pdf_vectors is not None:
            retriever = st.session_state.pdf_vectors.as_retriever()
            # ConversationalRetrievalChain 사용 시 LLM 객체 인자로 적당히 변경 필요
            from langchain.llms import OpenAI
            llm = OpenAI(temperature=0, openai_api_key=api_key, model_name="gpt-4.1-mini")

            qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever)

            result = qa_chain.run({"question": query, "chat_history": st.session_state.chat_history_pdf})
            st.session_state.chat_history_pdf.append((query, result))
            st.markdown(f"**답변:** {result}")
