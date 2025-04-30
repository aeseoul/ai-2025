import streamlit as st

st.set_page_config(page_title="GPT-4.1 Mini Web Chat", layout="centered")

st.title("💬 GPT-4.1 Mini Chat")
st.write("OpenAI API 키를 입력하고 질문해보세요!")

# ✅ API 키 입력받기 (숨김 처리)
api_key = st.text_input("🔑 OpenAI API Key", type="password")

# ✅ 질문 입력
question = st.text_area("📝 질문을 입력하세요", height=150)

# ✅ 제출 버튼
if st.button("GPT에 질문하기"):
    if not api_key:
        st.error("API 키를 입력해주세요.")
    elif not question.strip():
        st.error("질문을 입력해주세요.")
    else:
        # OpenAI API 호출
        try:
            openai.api_key = api_key

            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",  # 또는 gpt-4o
                messages=[{"role": "user", "content": question}],
                temperature=0.7
            )
            answer = response.choices[0].message.content
            st.success("✅ GPT의 응답:")
            st.write(answer)
        except Exception as e:
            st.error(f"⚠️ 에러 발생: {e}")
