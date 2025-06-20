# app.py

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from core.chat_chain import build_chat_chain
from core.embedding_utils import process_pdfs
from utils.history_manager import load_chat_history, save_chat_history
from utils.session_viewer import render_sidebar_history, export_chat_to_markdown
from utils.auth import login

load_dotenv()
st.set_page_config("RAG Chatbot", layout="wide")

# --- Auth ---
login()

st.title("📄 Conversational RAG PDF Chatbot")
st.caption("Chat with your PDFs, keep session history, and view source context.")

api_key = st.text_input("🔑 Enter Groq API Key", type="password")

if api_key:
    llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-V2")

    session_id = st.text_input("🆔 Session ID", value="default")
    uploaded_files = st.file_uploader("📎 Upload PDF files", type="pdf", accept_multiple_files=True)

    if "store" not in st.session_state:
        st.session_state.store = {}

    def get_history(session=session_id):
        if session not in st.session_state.store:
            st.session_state.store[session] = load_chat_history(session)
        return st.session_state.store[session]

    if uploaded_files:
        with st.spinner("🔍 Processing files and building context..."):
            retriever, source_map = process_pdfs(uploaded_files, embeddings)
            chat_chain = build_chat_chain(llm, retriever, get_history)

        # Render previous history
        history = get_history(session_id)
        for msg in history.messages:
            role = "user" if msg.type == "human" else "assistant"
            st.chat_message(role).write(msg.content)

        user_input = st.chat_input("💬 Ask a question")
        if user_input:
            with st.spinner("🤖 Generating answer..."):
                result = chat_chain.invoke({"input": user_input}, config={"configurable": {"session_id": session_id}})

                # Show rewritten question if changed
                if rewritten := result.get("standalone_question"):
                    st.info(f"🔁 Rewritten: {rewritten}")
                print(rewritten)
                # Show response
                st.chat_message("user").write(user_input)
                st.chat_message("assistant").write(result["answer"])
                save_chat_history(session_id, get_history(session_id))
                # Show sources
                if "source_documents" in result:
                    print(f"Content of source_documents: {result['source_documents']}") # Add this line
                    with st.expander("📚 Sources"):
                        st.write(result["source_documents"])
                    

# Sidebar tools
with st.sidebar:
    render_sidebar_history()
    st.markdown("---")
    if st.button("⬇️ Export Chat to Markdown"):
        markdown = export_chat_to_markdown(get_history(session_id).messages)
        st.download_button("Download", data=markdown, file_name=f"chat_{session_id}.md")
