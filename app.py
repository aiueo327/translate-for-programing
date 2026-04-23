import streamlit as st
import google.generativeai as genai

# --- 1. APIキーの設定（安全な方法） ---
try:
    # Streamlit Cloudの Secrets から安全に読み込む
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("APIキーが設定されていません。Streamlit CloudのSecrets設定を確認してください。")
    st.stop()

# ここが超重要：余計なオプションは一切つけない！
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. ページとデザインの設定 ---
st.set_page_config(page_title="Global Code Translator", layout="wide")

st.markdown("""
<style>
    .line-container { border-bottom: 1px solid #333; padding: 10px 0; display: flex; flex-direction: column; }
    .line-num { color: #666; font-family: monospace; font-size: 0.75em; margin-bottom: 2px; }
    .top-content { color: #00d4ff; font-family: 'Consolas', monospace; font-weight: bold; font-size: 1.1em; }
    .bottom-content { color: #e0e0e0; font-family: sans-serif; font-size: 0.95em; margin-top: 4px; line-height: 1.4; }
    .arrow { color: #ff4b4b; margin-right: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 グローバル・コード翻訳機")

# --- 3. サイドバーの設定 ---
with st.sidebar:
    st.header("🔧 翻訳設定")
    mode = st.radio("翻訳の方向", ["自然言語 ➔ コード", "コード ➔ 自然言語（解説）"])
    source_lang = st.selectbox("使用する言語", ["日本語", "English"])
    target_code = st.selectbox("プログラミング言語", ["Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "HTML/CSS"])

# --- 4. メインレイアウト ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 入力エリア")
    placeholder_msg = "日本語または英語で指示を入力..." if mode == "自然言語 ➔ コード" else "ソースコードを貼り付け..."
    user_input = st.text_area("Input", height=500, placeholder=placeholder_msg, label_visibility="collapsed")
    translate_btn = st.button("翻訳を実行 🚀", use_container_width=True)

with col2:
    st.subheader("📤 結果（行対比）")
    result_area = st.container(height=550, border=True)

    if translate_btn and user_input:
        with st.spinner("AIによる翻訳を実行中..."):
            try:
                # --- 5. モデルの指定（最もシンプルで安定した書き方） ---
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # プロンプト（指示書）の作成
                if mode == "自然言語 ➔ コード":
                    sys_prompt = f"入力された{source_lang}の各行を、対応する{target_code}のコードに1行ずつ翻訳してください。解説は不要。行数を完全に一致させてください。"
                else:
                    sys_prompt = f"入力された{target_code}の各行を、{source_lang}で1行ずつ簡潔に説明してください。行数を完全に一致させてください。"

                # AIの実行
                response = model.generate_content(f"{sys_prompt}\n\n入力データ:\n{user_input}")
                
                # 結果の表示処理
                input_lines = user_input.split('\n')
                output_lines = response.text.strip().split('\n')
                
                with result_area:
                    max_lines = max(len(input_lines), len(output_lines))
                    for i in range(max_lines):
                        in_txt = input_lines[i] if i < len(input_lines) else ""
                        out_txt = output_lines[i] if i < len(output_lines) else ""
                        
                        st.markdown(f"""
                        <div class="line-container">
                            <div class="line-num">LINE {i+1}</div>
                            <div class="top-content">{in_txt}</div>
                            <div class="bottom-content"><span class="arrow">↳</span>{out_txt}</div>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                # エラーが起きた場合のメッセージ
                error_msg = str(e)
                st.error("エラーが発生しました。")
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    st.warning("⚠️ 無料枠の制限に達しました。1分ほど待ってから再度実行してください。")
                else:
                    st.code(error_msg)
    else:
        with result_area:
            st.info("左側に入力して「翻訳を実行」を押してください。")