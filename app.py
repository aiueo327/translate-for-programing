import streamlit as st
import google.generativeai as genai

# --- 設定 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # あなたのキーをそのまま使用
    GOOGLE_API_KEY = "AIzaSyC4EAcrRMjKRxUqw7Kt1LVTY3CeRYbbJC0"

genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Global Code Translator", layout="wide")

# CSS: デザイン
st.markdown("""
<style>
    .line-container { border-bottom: 1px solid #333; padding: 8px 0; display: flex; flex-direction: column; }
    .line-num { color: #666; font-family: monospace; font-size: 0.75em; margin-bottom: 2px; }
    .top-content { color: #00d4ff; font-family: 'Consolas', monospace; font-weight: bold; }
    .bottom-content { color: #e0e0e0; font-family: sans-serif; font-size: 0.95em; margin-top: 4px; }
    .arrow { color: #ff4b4b; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 グローバル・コード翻訳機")

with st.sidebar:
    st.header("🔧 設定")
    mode = st.radio("翻訳の方向", ["自然言語 ➔ コード", "コード ➔ 自然言語（解説）"])
    source_lang = st.selectbox("言語", ["日本語", "English"])
    target_code = st.selectbox("対象", ["Python", "JavaScript", "TypeScript", "HTML/CSS"])

# --- メインレイアウト ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 入力")
    user_input = st.text_area("Input", height=500, placeholder="ここに貼り付け...", label_visibility="collapsed")
    translate_btn = st.button("翻訳を実行 🚀", use_container_width=True)

with col2:
    st.subheader("📤 結果")
    result_area = st.container(height=550, border=True)

    if translate_btn and user_input:
        # --- Zenn の記事に基づいた修正：明示的にフルパスを指定 ---
        # "models/gemini-1.5-flash" と書くことで、古いデフォルト設定を上書きします
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        
        if mode == "自然言語 ➔ コード":
            sys_prompt = f"入力された{source_lang}の行に対応する{target_code}のコードを1行ずつ出力せよ。解説不要。行数を一致させよ。"
        else:
            sys_prompt = f"入力された{target_code}の各行を{source_lang}で1行ずつ簡潔に説明せよ。行数を一致させよ。"

        with st.spinner("解析中..."):
            try:
                response = model.generate_content(f"{sys_prompt}\n\n入力:\n{user_input}")
                
                input_lines = user_input.split('\n')
                output_lines = response.text.strip().split('\n')
                
                with result_area:
                    max_lines = max(len(input_lines), len(output_lines))
                    for i in range(max_lines):
                        in_txt = input_lines[i] if i < len(input_lines) else ""
                        out_txt = output_lines[i] if i < len(output_lines) else ""
                        
                        st.markdown(f"""
                        <div class="line-container">
                            <div class="line-num">Line {i+1}</div>
                            <div class="top-content">{in_txt}</div>
                            <div class="bottom-content"><span class="arrow">↳</span>{out_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")