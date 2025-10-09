# gui.py
import tkinter as tk
from tkinter import scrolledtext
from ai_vibe_chat.engine import Engine
from ai_vibe_chat.providers.local_rules import LocalRulesProvider
from ai_vibe_chat.personalities.rizz import RizzPersonality
import re

def strip_ansi_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
    return ansi_escape.sub('', text)

engine = Engine(LocalRulesProvider(), RizzPersonality())

root = tk.Tk()
root.title("RizzBot Chat 🕶️")
root.geometry("650x650")
root.configure(bg="#1e1e2f")

# --- Chat Display ---
chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled",
                                         bg="#1e1e2f", fg="#ffffff",
                                         font=("Helvetica", 13), padx=10, pady=10)
chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_display.tag_config("user", foreground="#a8ff60", justify="right", spacing3=10)
chat_display.tag_config("greeting", foreground="#32cd32", spacing3=10)
chat_display.tag_config("motivation", foreground="#f5e05a", spacing3=10)
chat_display.tag_config("technical", foreground="#00ffff", spacing3=10)
chat_display.tag_config("general", foreground="#ff69b4", spacing3=10)

# --- Input Frame ---
input_frame = tk.Frame(root, bg="#1e1e2f")
input_frame.pack(fill=tk.X, padx=10, pady=5)
user_input = tk.Entry(input_frame, font=("Helvetica", 14), bg="#2e2e3f", fg="#ffffff",
                      insertbackground="#ffffff", relief="groove", bd=3)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5), ipady=8)
send_button = tk.Button(input_frame, text="Send", bg="#4e4e6a", fg="#ffffff", font=("Helvetica", 12, "bold"),
                        command=lambda: send_message())
send_button.pack(side=tk.RIGHT, ipadx=10, ipady=5)

# --- Send / Receive Function ---
def send_message():
    msg = user_input.get().strip()
    if not msg:
        return
    user_input.delete(0, tk.END)
    append_message(f"You: {msg}", "user")
    bot_response = engine.respond(msg)
    clean_response = strip_ansi_codes(bot_response)
    append_message(f"Bot: {clean_response}", categorize_response(msg))

def append_message(message, tag="general"):
    chat_display.configure(state="normal")
    chat_display.insert(tk.END, message + "\n\n", tag)
    chat_display.configure(state="disabled")
    chat_display.yview(tk.END)

# --- Categorize response based on keywords ---
def categorize_response(text: str) -> str:
    text_lower = text.lower()
    if any(word in text_lower for word in ["hi", "hello", "hey", "hiya"]):
        return "greeting"
    elif any(word in text_lower for word in ["gym", "workout", "lift", "exercise"]):
        return "motivation"
    elif any(word in text_lower for word in ["recursion", "function", "code", "program"]):
        return "technical"
    elif any(word in text_lower for word in ["how are you", "what's up", "how's it going"]):
        return "general"
    else:
        return "general"

root.bind("<Return>", lambda event=None: send_message())

append_message("🤖 RizzBot is online! Say hi 😎", "general")
root.mainloop()




