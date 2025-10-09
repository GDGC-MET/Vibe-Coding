# ai_vibe_chat/engine.py
import argparse
from colorama import init, Fore, Style
from ai_vibe_chat import memory
from .providers.local_rules import LocalRulesProvider
from .personalities.rizz import RizzPersonality

# Initialize colorama
init(autoreset=True)

# CLI Memory Flag
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--memory", action="store_true", help="Enable conversation memory")
_args, _ = parser.parse_known_args()
ENABLE_MEMORY = _args.memory

class Engine:
    def __init__(self, provider, personality):
        self.provider = provider
        self.personality = personality

    def respond(self, user_text: str, user_id: str = "default_user"):
        if not user_text.strip():
            return "Say something fun, I’m listening 😉"

        # Memory load
        if ENABLE_MEMORY:
            current_memory = memory.load_memory()
            user_convo = current_memory.get(user_id, [])
        else:
            user_convo = []

        # Provider response
        raw_response, category = self.provider.generate(user_text)

        # Personality styling
        styled_response = self.personality.style_response(raw_response, category)

        # Memory update
        if ENABLE_MEMORY:
            memory.add_to_memory(user_id, "user", user_text, category)
            memory.add_to_memory(user_id, "bot", styled_response, category)

        # Colored CLI output
        color_map = {
            "greeting": Fore.GREEN,
            "motivation": Fore.YELLOW,
            "technical": Fore.CYAN,
            "joke": Fore.MAGENTA,
            "advice": Fore.BLUE,
            "general": Fore.WHITE
        }
        color = color_map.get(category, Fore.WHITE)
        return f"{color}{styled_response}{Style.RESET_ALL}"

if __name__ == "__main__":
    engine = Engine(LocalRulesProvider(), RizzPersonality())
    print("🤖 Chat started (Ctrl+C to exit) — RizzBot with Memory Enabled!\n")
    while True:
        try:
            user_input = input("You: ")
            response = engine.respond(user_input)
            print("Bot:", response)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat. Stay smooth 😎")
            break

