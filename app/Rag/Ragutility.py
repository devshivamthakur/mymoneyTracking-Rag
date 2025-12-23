import json
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
import os
from collections import deque

folder = "ChatHistory"
os.makedirs(folder, exist_ok=True)  # ✅ Create folder if missing

MAX_CHATS_PER_USER = 10

def save_messages_jsonl(human_msg: HumanMessage, ai_msg: AIMessage, userId: str):
    file_path = f"{folder}/chat_history_{userId}.jsonl"
    
    # Load existing history
    existing_history = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    existing_history.append(record)
                except json.JSONDecodeError:
                    continue
    
    # Create new entry
    new_entry = {
        "timestamp": str(datetime.now()),
        "messages": [
            {"role": "human", "content": human_msg.content},
            {"role": "ai", "content": ai_msg.content}
        ]
    }
    
    # Add new entry and keep only the last MAX_CHATS_PER_USER entries
    existing_history.append(new_entry)
    
    # Keep only the most recent entries
    if len(existing_history) > MAX_CHATS_PER_USER:
        existing_history = existing_history[-MAX_CHATS_PER_USER:]
    
    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        for entry in existing_history:
            f.write(json.dumps(entry) + "\n")

def load_messages_jsonl(userId: str):
    file_path = f"{folder}/chat_history_{userId}.jsonl"
    history = []
    
    if not os.path.exists(file_path):
        return history
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                for msg in record["messages"]:
                    if msg["role"] == "human":
                        history.append(HumanMessage(content=msg["content"]))
                    else:
                        history.append(AIMessage(content=msg["content"]))
            except json.JSONDecodeError:
                continue
    return history

def clear_chat_history(userId: str) -> bool:
    """
    Clear ALL chat history for a specific user.
    Returns True if successful, False if no history exists.
    """
    file_path = f"{folder}/chat_history_{userId}.jsonl"
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error clearing chat history for user {userId}: {e}")
            return False
    return False

DEFAULT_FIREBASE_FILTER = {'isQueryToAppFinanceRelated': False}