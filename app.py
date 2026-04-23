import streamlit as st
import google.generativeai as genai

# --- 1. API設定 ---
try:
    # これからは「Secrets」という安全な場所からキーを読み込みます
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # ここに直接キーを書き込むのはやめましょう！
    st.error("APIキーが設定されていません。StreamlitのSecretsに登録してください。")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
# ページ設定
st.set_page_config(page_title="Global Code Translator", layout="wide")

# --- 2. デザイン (CSS) ---
st.markdown("""
<style>
    .line-container { border-bottom: 1px solid #333; padding: 10px 0; display: flex; flex-direction: column; }
    .line-num { color: #666; font-family: monospace; font-size: 0.75em; margin-bottom: 2px; }
    .top-content { color: #00d4ff; font-family: 'Consolas', monospace; font-weight: bold; font-size: 1.1em; }
    .bottom-content { color: #e0e0e0; font-family: sans-serif; font-size: 0.95em; margin-top: 4px; line-height: 1.4; }
    .arrow { color: #ff4b4b; margin-right: 8px; font-weight: bold; }
    .stTextArea textarea { font-family: monospace; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 グローバル・コード翻訳機")
st.caption("行ごとに対比させて、プログラムと自然言語を翻訳します。")

# --- 3. サイドバー設定 ---
with st.sidebar:
    st.header("🔧 翻訳設定")
    mode = st.radio("翻訳の方向", ["自然言語 ➔ コード", "コード ➔ 自然言語（解説）"])
    source_lang = st.selectbox("使用する言語", ["日本語", "English"])
    target_code = st.selectbox("プログラミング言語", ["Python", "JavaScript", "TypeScript", "Java", "C++", "SQL", "HTML/CSS"])
    
    st.divider()
    st.info("404エラー対策のため、利用可能なモデルを自動選択する機能を搭載しています。")

# --- 4. メインレイアウト ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 入力エリア")
    placeholder_msg = "日本語または英語で指示を入力..." if mode == "自然言語 ➔ コード" else "ソースコードを貼り付け..."
    user_input = st.text_area("Input", height=500, placeholder=placeholder_msg, label_visibility="collapsed")
    translate_btn = st.button("翻訳・解析を実行 🚀", use_container_width=True)

with col2:
    st.subheader("📤 結果（行対比）")
    result_area = st.container(height=550, border=True)

    if translate_btn and user_input:
        with st.spinner("利用可能な最適なAIモデルを探しています..."):
            try:
                # --- エラー回避の核心：利用可能なモデルをリストアップ ---
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # 優先順位をつけてモデルを決定
                target_model = ""
                priority_list = [
                    "models/gemini-1.5-flash",
                    "models/gemini-1.5-flash-latest",
                    "models/gemini-2.0-flash",
                    "models/gemini-1.5-pro"
                ]
                
                for p in priority_list:
                    if p in available_models:
                        target_model = p
                        break
                
                if not target_model and available_models:
                    target_model = available_models[0]
                
                if not target_model:
                    st.error("利用可能なGeminiモデルが見つかりませんでした。APIキーの有効性を確認してください。")
                    st.stop()

                # モデルの初期化
                model = genai.GenerativeModel(model_name=target_model)
                
                # プロンプト作成
                if mode == "自然言語 ➔ コード":
                    sys_prompt = f"あなたはプログラミング翻訳機です。入力された{source_lang}の各行を、対応する{target_code}のコードに1行ずつ翻訳してください。解説は一切含めず、入力と同じ行数で出力してください。"
                else:
                    sys_prompt = f"あなたはコード解説者です。入力された{target_code}の各行を、{source_lang}で1行ずつ簡潔に説明してください。入力のコード1行に対して、説明を必ず1行返し、行数を完全に一致させてください。"

                # AI呼び出し
                response = model.generate_content(f"{sys_prompt}\n\n入力データ:\n{user_input}")
                
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
                
                # ダウンロードボタン
                st.download_button(
                    label="📄 結果を保存",
                    data=response.text,
                    file_name=f"translated_output.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                if "429" in str(e):
                    st.warning("無料枠の制限に達しました。1分ほど待ってから再度実行してください。")
    else:
        with result_area:
            st.info("左側に入力して「翻訳を実行」を押してください。")