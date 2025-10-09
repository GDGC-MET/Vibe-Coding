# ai_vibe_chat/providers/local_rules.py
import re
import random
from ai_vibe_chat import memory

class LocalRulesProvider:
    name = "local-rules"

    def __init__(self):
        self._greetings = [
            "Hello! How can I help?",
            "Hey there! What's vibing?",
            "Hi! Good to see you!"
        ]
        self._motivation = [
            "Push one more rep. Future you says thanks.",
            "Consistency beats intensity. Show up.",
            "You don't skip leg day, do you?"
        ]
        self._technical = [
            "A thing defined in terms of a smaller version of itself.",
            "Recursive functions call themselves, you know?"
        ]
        self._jokes = [
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "Debugging is like being a detective in a crime movie where you are also the murderer."
        ]
        self._advice = [
            "Stay hydrated, my friend.",
            "Sleep well, it fuels your brainpower."
        ]
        self._easter_eggs = {
            "tell me a secret": "🤫 I can’t tell everyone, but you’re awesome!",
            "rizz me up": "🔥 Rizz mode activated! Smooth operator!"
        }

    def generate(self, text: str):
        text_lower = text.lower()

        # Greetings
        if re.search(r"\b(hello|hi|hey|hiya)\b", text_lower):
            return random.choice(self._greetings), "greeting"

        # Motivation / Fitness
        if re.search(r"\b(gym|lift|workout|exercise|fitness)\b", text_lower):
            return random.choice(self._motivation), "motivation"

        # Technical / Recursion
        if re.search(r"\b(recursion|recursive|function|code|programming)\b", text_lower):
            return random.choice(self._technical), "technical"

        # Jokes
        if re.search(r"\b(joke|funny|laugh)\b", text_lower):
            return random.choice(self._jokes), "joke"

        # Advice
        if re.search(r"\b(advice|tip|help)\b", text_lower):
            return random.choice(self._advice), "advice"

        # Easter eggs
        for key in self._easter_eggs:
            if key in text_lower:
                return self._easter_eggs[key], "general"
            
            # Add this under Memory-aware queries / Fallback in generate()
            # --- Casual conversation ---
        if re.search(r"\b(how are you|what's up|how's it going|how you doing)\b", text_lower):
              return random.choice([
            "I'm vibing! Hope you are too 😎",
            "Feeling smooth today! How about you? 😉",
             "All good on my side! Stay awesome 😎"
          ]), "general"

            # Fun category
        if re.search(r"\b(joke|funny|riddle)\b", text_lower):
             return random.choice([
        "Why do programmers prefer dark mode? Because light attracts bugs! 😏",
        "I would tell you a recursion joke, but you'd just call it again… 😎",
    ]), "fun"

         
        # Memory-aware queries
        if re.search(r"\bwhat did we talk(ed)? about\b", text_lower) \
                or re.search(r"\bremind me\b", text_lower) \
                or re.search(r"\brecall\b", text_lower) \
                or "remember" in text_lower:
            summary = memory.get_summary("default_user")
            if summary:
                return f"We talked about: {summary}", "general"
            return "We haven't talked about much yet.", "general"

        # Fallback
        return "Tell me more about that.", "general"
