"""
Streamlit UI for the AI Video Assistant.

This file is a UI layer only — it imports and calls run_pipeline() and
ask_question() from your existing pipeline.py without modifying any core
logic. Drop this alongside pipeline.py (same folder, so the utils/ and
core/ imports resolve) and run:

    streamlit run app.py
"""

import io
import os
import sys
import tempfile
import contextlib
from datetime import datetime

import streamlit as st

from dotenv import load_dotenv
load_dotenv()

from main import run_pipeline
from core.rag_engine import ask_question


# --------------------------------------------------------------------------
# Page config + theme
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DARK_CSS = """
<style>
    .stApp {
        background-color: #0e1117;
        color: #e6e6e6;
    }
    section[data-testid="stSidebar"] {
        background-color: #12151c;
        border-right: 1px solid #262b36;
    }
    .step-log {
        background-color: #12151c;
        border: 1px solid #262b36;
        border-radius: 8px;
        padding: 14px 16px;
        font-family: 'SF Mono', 'Consolas', monospace;
        font-size: 13px;
        line-height: 1.6;
        max-height: 260px;
        overflow-y: auto;
        color: #9fe6a0;
        white-space: pre-wrap;
    }
    .result-card {
        background-color: #161a23;
        border: 1px solid #262b36;
        border-radius: 10px;
        padding: 20px 22px;
        margin-bottom: 12px;
    }
    .title-banner {
        background: linear-gradient(90deg, #1f2430, #161a23);
        border: 1px solid #2d3340;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 20px;
    }
    div[data-testid="stChatMessage"] {
        background-color: #161a23;
        border: 1px solid #262b36;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #2b6cb0;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #2c5282;
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Helper: live step tracker via stdout interception
# --------------------------------------------------------------------------
class StreamlitLogStream(io.StringIO):
    """Intercepts print() calls from the pipeline and streams them into a
    Streamlit placeholder in real time, without touching pipeline.py."""

    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.lines = []

    def write(self, s):
        if s.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.lines.append(f"[{timestamp}] {s.strip()}")
            self.placeholder.markdown(
                f'<div class="step-log">{"<br>".join(self.lines)}</div>',
                unsafe_allow_html=True,
            )
        return super().write(s)

    def flush(self):
        pass


def run_pipeline_with_live_log(source: str, language: str, placeholder):
    stream = StreamlitLogStream(placeholder)
    with contextlib.redirect_stdout(stream):
        result = run_pipeline(source, language=language)
    return result


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processing" not in st.session_state:
    st.session_state.processing = False


# --------------------------------------------------------------------------
# Sidebar — inputs
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎬 AI Video Assistant")
    st.caption("YouTube / local video → transcript → summary → chat")

    st.markdown("---")

    input_mode = st.radio("Source type", ["YouTube URL", "Local file"], horizontal=True)

    source_value = None
    if input_mode == "YouTube URL":
        source_value = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
    else:
        uploaded = st.file_uploader(
            "Upload audio/video file",
            type=["mp4", "mkv", "mov", "mp3", "wav", "m4a"],
        )
        if uploaded is not None:
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, uploaded.name)
            with open(tmp_path, "wb") as f:
                f.write(uploaded.getbuffer())
            source_value = tmp_path
            st.success(f"Ready: {uploaded.name}")

    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    st.markdown("---")

    run_clicked = st.button(
        "▶ Run Pipeline",
        use_container_width=True,
        disabled=st.session_state.processing or not source_value,
    )

    if st.session_state.result:
        st.markdown("---")
        if st.button("🗑 Clear results", use_container_width=True):
            st.session_state.result = None
            st.session_state.chat_history = []
            st.rerun()


# --------------------------------------------------------------------------
# Main area
# --------------------------------------------------------------------------
st.markdown("# Video → Insights → Chat")

if run_clicked and source_value:
    st.session_state.processing = True
    st.session_state.chat_history = []

    st.markdown("### Processing")
    log_placeholder = st.empty()

    with st.spinner("Running pipeline — this can take a while for long videos..."):
        try:
            result = run_pipeline_with_live_log(source_value, language, log_placeholder)
            st.session_state.result = result
            st.success("Done! Scroll down for results.")
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
        finally:
            st.session_state.processing = False

result = st.session_state.result

if result:
    st.markdown(
        f'<div class="title-banner"><h3>📌 {result["title"]}</h3></div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        ["📝 Summary", "✅ Action Items", "📋 Key Decisions", "❓ Open Questions", "📄 Transcript", "💬 Chat"]
    )

    with tabs[0]:
        st.markdown(f'<div class="result-card">{result["summary"]}</div>', unsafe_allow_html=True)

    with tabs[1]:
        st.markdown(f'<div class="result-card">{result["action_item"]}</div>', unsafe_allow_html=True)

    with tabs[2]:
        st.markdown(f'<div class="result-card">{result["key_decisions"]}</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown(f'<div class="result-card">{result["open_questions"]}</div>', unsafe_allow_html=True)

    with tabs[4]:
        st.markdown(f'<div class="result-card">{result["transcript"]}</div>', unsafe_allow_html=True)

    with tabs[5]:
        st.caption("Ask questions about the video content, grounded in the transcript via RAG.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        question = st.chat_input("Ask something about this video...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = ask_question(result["rag_chain"], question)
                    except Exception as e:
                        answer = f"Error answering question: {e}"
                    st.write(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # ----------------------------------------------------------------
    # Downloadable report
    # ----------------------------------------------------------------
    report_text = (
        f"AI VIDEO ASSISTANT REPORT\n"
        f"{'=' * 60}\n"
        f"Title: {result['title']}\n\n"
        f"SUMMARY\n{'-' * 40}\n{result['summary']}\n\n"
        f"ACTION ITEMS\n{'-' * 40}\n{result['action_item']}\n\n"
        f"KEY DECISIONS\n{'-' * 40}\n{result['key_decisions']}\n\n"
        f"OPEN QUESTIONS\n{'-' * 40}\n{result['open_questions']}\n\n"
        f"TRANSCRIPT\n{'-' * 40}\n{result['transcript']}\n"
    )

    st.download_button(
        "⬇ Download full report (.txt)",
        data=report_text,
        file_name=f"{result['title'][:50].strip().replace(' ', '_') or 'report'}.txt",
        mime="text/plain",
        use_container_width=False,
    )

elif not run_clicked:
    st.info("Enter a YouTube URL or upload a local file in the sidebar, then click **Run Pipeline**.")
