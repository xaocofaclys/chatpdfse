# utils/history_manager.py

import os
import json
from langchain_community.chat_message_histories import ChatMessageHistory

HISTORY_DIR = "data/histories"
os.makedirs(HISTORY_DIR, exist_ok=True)

def save_chat_history(session_id, history: ChatMessageHistory):
    path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    data = [
        {"type": msg.type, "content": msg.content}
        for msg in history.messages
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_chat_history(session_id) -> ChatMessageHistory:
    history = ChatMessageHistory()
    path = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if item["type"] == "human":
                    history.add_user_message(item["content"])
                elif item["type"] == "ai":
                    history.add_ai_message(item["content"])
    return history

def list_sessions():
    return [f.replace(".json", "") for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]

def export_chat_to_markdown(messages):
    markdown = ""
    for msg in messages:
        if msg.type == "human":
            markdown += f"**User:** {msg.content}\n\n"
        elif msg.type == "ai":
            markdown += f"**Assistant:** {msg.content}\n\n"
    return markdown
