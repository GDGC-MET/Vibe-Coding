# ai_vibe_chat/memory.py
import json
from pathlib import Path

MEMORY_FILE = Path("conversation_memory.json")

def load_memory() -> dict:
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory_data: dict) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=2)

def add_to_memory(user_id: str, role: str, text: str, category: str) -> None:
    memory_data = load_memory()
    if user_id not in memory_data:
        memory_data[user_id] = []
    memory_data[user_id].append({
        "role": role,
        "text": text,
        "category": category
    })
    save_memory(memory_data)

def get_summary(user_id: str, last_n: int = 5) -> str:
    memory_data = load_memory()
    if user_id not in memory_data or not memory_data[user_id]:
        return ""
    
    recent = memory_data[user_id][-last_n:]
    texts = [entry["text"] for entry in recent if entry["role"] == "user"]
    # remove duplicates while preserving order
    seen = set()
    summary = []
    for t in texts:
        if t.lower() not in seen:
            seen.add(t.lower())
            summary.append(t)
    return ", ".join(summary)
