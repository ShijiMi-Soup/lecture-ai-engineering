# app.py
import data  # データモジュール
import database  # データベースモジュール
import llm  # LLMモジュール
import metrics  # 評価指標モジュール
import streamlit as st
import torch
import ui  # UIモジュール
from config import MODEL_NAME
from transformers import pipeline

# --- アプリケーション設定 ---
st.set_page_config(page_title="Gemma Chatbot", layout="wide")

# --- 初期化処理 ---
# NLTKデータのダウンロード（初回起動時など）
metrics.initialize_nltk()

# データベースの初期化（テーブルが存在しない場合、作成）
database.init_db()

# データベースが空ならサンプルデータを投入
data.ensure_initial_data()


# LLMモデルのロード（キャッシュを利用）
# モデルをキャッシュして再利用
@st.cache_resource
def load_model():
    """LLMモデルをロードする"""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.toast(f"Using device: {device}")  # 使用デバイスを表示
        pipe = pipeline(
            "text-generation",
            model=MODEL_NAME,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=device,
        )
        st.toast(f"モデル '{MODEL_NAME}' の読み込みに成功しました。", icon="✅")
        return pipe
    except Exception as e:
        st.toast(f"モデル '{MODEL_NAME}' の読み込みに失敗しました: {e}", icon="❌")
        st.toast(
            "GPUメモリ不足の可能性があります。不要なプロセスを終了するか、より小さいモデルの使用を検討してください。",
            icon="❌",
        )
        return None


pipe = llm.load_model()

# --- Streamlit アプリケーション ---
st.title("🤖 Gemma 2 Chatbot with Feedback")
st.write(
    "Gemmaモデルを使用したチャットボットです。回答に対してフィードバックを行えます。"
)
st.markdown("---")

# --- サイドバー ---
st.sidebar.title("ナビゲーション")
# セッション状態を使用して選択ページを保持
if "page" not in st.session_state:
    st.session_state.page = "チャット"  # デフォルトページ

page = st.sidebar.radio(
    "ページ選択",
    ["チャット", "履歴閲覧", "サンプルデータ管理"],
    key="page_selector",
    index=["チャット", "履歴閲覧", "サンプルデータ管理"].index(
        st.session_state.page
    ),  # 現在のページを選択状態にする
    on_change=lambda: setattr(
        st.session_state, "page", st.session_state.page_selector
    ),  # 選択変更時に状態を更新
)


# --- メインコンテンツ ---
if st.session_state.page == "チャット":
    if pipe:
        ui.display_chat_page(pipe)
    else:
        st.toast(
            "チャット機能を利用できません。モデルの読み込みに失敗しました。", icon="❌"
        )
elif st.session_state.page == "履歴閲覧":
    ui.display_history_page()
elif st.session_state.page == "サンプルデータ管理":
    ui.display_data_page()

# --- フッターなど（任意） ---
st.sidebar.markdown("---")
st.sidebar.info("開発者: [Your Name]")
