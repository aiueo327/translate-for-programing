import streamlit as st
import google.generativeai as genai

# --- 設定エリア ---
# さっき取得した自分のAPIキーを "" の中に入れてください
GOOGLE_API_KEY = "AIzaSyC4EAcrRMjKRxUqw7Kt1LVTY3CeRYbbJC0"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="マイGeminiチャット", layout="centered")
st.title("🤖 マイGemini AI")

# --- チャット履歴の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 履歴の表示 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- チャット入力欄 ---
if prompt := st.chat_input("何でも聞いてね"):
    # ユーザーの入力を履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Geminiからの回答を生成
    with st.chat_message("assistant"):
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.markdown(response.text)
    
    # 回答を履歴に追加
    st.session_state.messages.append({"role": "assistant", "content": response.text})