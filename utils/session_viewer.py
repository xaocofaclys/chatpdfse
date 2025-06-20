# utils/session_viewer.py

import streamlit as st
import os
import json
from utils.history_manager import list_sessions, load_chat_history

def render_sidebar_history():
    st.header("📜 History Viewer")
    sessions = list_sessions()
    if sessions:
        session_selected = st.selectbox("Select session", sessions)
        history = load_chat_history(session_selected)
        for msg in history.messages:
            if msg.type == "human":
                st.markdown(f"**🧑 You:** {msg.content}")
            elif msg.type == "ai":
                st.markdown(f"**🤖 Assistant:** {msg.content}")
    else:
        st.info("No saved sessions yet.")

def export_chat_to_markdown(messages):
    markdown = ""
    for msg in messages:
        if msg.type == "human":
            markdown += f"**User:** {msg.content}\n\n"
        elif msg.type == "ai":
            markdown += f"**Assistant:** {msg.content}\n\n"
    return markdown
