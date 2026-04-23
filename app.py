import streamlit as st
import google.generativeai as genai

# --- 設定 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "AIzaSyC4EAcrRMjKRxUqw7Kt1LVTY3CeRYbbJC0"

genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="Global Code Translator", layout="wide")

# CSS: デザインの微調整
st.markdown("""
<style>
    .line-container { border-bottom: 1px solid #333; padding: 8px 0; display: flex; flex-direction: column; }
    .line-num { color: #666; font-family: monospace; font-size: 0.75em; margin-bottom: 2px; text-transform: uppercase; }
    .top-content { color: #00d4ff; font-family: 'Consolas', monospace; font-weight: bold; font-size: 1.05em; }
    .bottom-content { color: #e0e0e0; font-family: sans-serif; font-size: 0.95em; line-height: 1.4; margin-top: 4px; }
    .arrow { color: #ff4b4b; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 グローバル・コード翻訳機")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("🔧 翻訳設定")
    
    # 1. 何を何に変えるか
    mode = st.radio("翻訳の方向", ["自然言語 ➔ コード", "コード ➔ 自然言語（解説）"])
    
    # 2. 自然言語の選択（英語を追加！）
    source_lang = st.selectbox("使用する言語（日本語/英語）", ["日本語", "English"])
    
    # 3. プログラミング言語の選択
    target_code = st.selectbox("プログラミング言語", ["Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "HTML/CSS"])
    
    st.divider()
    st.caption("※行数を一致させて対比表示します")

# --- メインレイアウト ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 入力")
    placeholder_txt = "ここに指示、またはコードを入力してください..."
    user_input = st.text_area("Input Area", height=500, placeholder=placeholder_txt, label_visibility="collapsed")
    translate_btn = st.button("翻訳を実行 🚀", use_container_width=True)

with col2:
    st.subheader("📤 結果（行対比）")
    result_area = st.container(height=550, border=True)

    if translate_btn and user_input:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # モードと選択言語に応じた指示（プロンプト）の動的生成
        if mode == "自然言語 ➔ コード":
            sys_prompt = f"入力された{source_lang}の行に対応する{target_code}のコードを1行ずつ出力してください。解説は一切不要。行数を厳格に一致させること。"
        else:
            sys_prompt = f"入力された{target_code}の各行を、{source_lang}で非常に簡潔に説明してください。1行のコードに対して1行の説明を返し、行数を完全に一致させてください。"

        with st.spinner("AIによる多言語解析中..."):
            try:
                response = model.generate_content(f"{sys_prompt}\n\n入力データ:\n{user_input}")
                
                input_lines = user_input.split('\n')
                output_lines = response.text.strip().split('\n')
                
                with result_area:
                    max_lines = max(len(input_lines), len(output_lines))
                    for i in range(max_lines):
                        in_txt = input_lines[i] if i < len(input_lines) else ""
                        out_txt = output_lines[i] if i < len(output_lines) else ""
                        
                        # ビジュアル表示
                        st.markdown(f"""
                        <div class="line-container">
                            <div class="line-num">Line {i+1}</div>
                            <div class="top-content">{in_txt}</div>
                            <div class="bottom-content"><span class="arrow">↳</span>{out_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        with result_area:
            st.info("左側に入力して実行してください。")