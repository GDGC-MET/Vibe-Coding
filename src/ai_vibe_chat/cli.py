from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Type

import click
from colorama import Fore, Style, init as colorama_init

from .engine import Engine
from .personalities import RizzPersonality, SarcasticPersonality
from .providers import LocalRulesProvider

try:
    from .providers import HuggingFaceProvider, HuggingFaceChatProvider
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


PERSONALITIES: Dict[str, Type] = {
    "rizz": RizzPersonality,
    "sarcastic": SarcasticPersonality,
}


class ConversationHistory:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, speaker: str, text: str, timestamp: str = None):
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append({
            "speaker": speaker,
            "text": text,
            "timestamp": timestamp
        })
    
    def clear(self):
        self.messages.clear()
    
    def save_to_file(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.messages = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False


def _print_user(text: str, timestamp: str = None) -> None:
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
    click.echo(f"{Fore.BLUE}[{timestamp}]{Style.RESET_ALL} {Fore.CYAN}You:{Style.RESET_ALL} {text}")


def _print_bot(name: str, text: str, timestamp: str = None) -> None:
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
    click.echo(f"{Fore.BLUE}[{timestamp}]{Style.RESET_ALL} {Fore.MAGENTA}{name}:{Style.RESET_ALL} {text}")


def _show_typing_indicator():
    """Show a typing indicator animation"""
    for i in range(3):
        click.echo(f"{Fore.YELLOW}Bot is typing{'...'[:i+1]}{Style.RESET_ALL}", nl=False)
        time.sleep(0.3)
        click.echo("\r" + " " * 20 + "\r", nl=False)  # Clear line
    click.echo("\r" + " " * 20 + "\r", nl=False)  # Final clear


def _show_help():
    """Display help information"""
    click.echo(f"\n{Fore.GREEN}Available Commands:{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}/help{Style.RESET_ALL}     - Show this help message")
    click.echo(f"{Fore.CYAN}/clear{Style.RESET_ALL}    - Clear conversation history")
    click.echo(f"{Fore.CYAN}/save <file>{Style.RESET_ALL} - Save conversation to file")
    click.echo(f"{Fore.CYAN}/load <file>{Style.RESET_ALL} - Load conversation from file")
    click.echo(f"{Fore.CYAN}/quit{Style.RESET_ALL}     - Exit the chat")
    click.echo(f"{Fore.CYAN}/exit{Style.RESET_ALL}     - Exit the chat")
    click.echo()


def _process_command(command: str, history: ConversationHistory) -> bool:
    """Process special commands. Returns True if command was processed, False otherwise."""
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == "/help":
        _show_help()
        return True
    elif cmd == "/clear":
        history.clear()
        click.echo(f"{Fore.GREEN}Conversation history cleared!{Style.RESET_ALL}")
        return True
    elif cmd == "/save":
        if len(parts) < 2:
            click.echo(f"{Fore.RED}Usage: /save <filename>{Style.RESET_ALL}")
            return True
        filename = parts[1]
        history.save_to_file(filename)
        click.echo(f"{Fore.GREEN}Conversation saved to {filename}!{Style.RESET_ALL}")
        return True
    elif cmd == "/load":
        if len(parts) < 2:
            click.echo(f"{Fore.RED}Usage: /load <filename>{Style.RESET_ALL}")
            return True
        filename = parts[1]
        if history.load_from_file(filename):
            click.echo(f"{Fore.GREEN}Conversation loaded from {filename}!{Style.RESET_ALL}")
            # Display loaded messages
            for msg in history.messages:
                if msg["speaker"] == "You":
                    _print_user(msg["text"], msg["timestamp"])
                else:
                    _print_bot(msg["speaker"], msg["text"], msg["timestamp"])
        else:
            click.echo(f"{Fore.RED}Failed to load conversation from {filename}!{Style.RESET_ALL}")
        return True
    
    return False


@click.command()
@click.option("--personality", "personality_name", default="rizz", show_default=True)
@click.option("--provider", "provider_name", default="local", show_default=True, 
              type=click.Choice(["local"] + (["huggingface", "huggingface-chat"] if HF_AVAILABLE else [])),
              help="Choose AI provider: local (rules)" + (", huggingface (real AI), huggingface-chat (chat model)" if HF_AVAILABLE else " (HuggingFace providers not available - install torch/transformers)"))
@click.option("--model", "model_name", default="meta-llama/Llama-2-7b-chat-hf", 
              help="Hugging Face model name (only for AI providers)")
@click.option(
    "--inject-error",
    "inject_error",
    type=click.Choice(["startup", "personality", "provider", "response"], case_sensitive=False),
    default=None,
    help="Inject a controlled error for testing: startup | personality | provider | response",
)
def main(personality_name: str, provider_name: str, model_name: str, inject_error: str | None = None) -> None:
    colorama_init(autoreset=True)

    PersonalityCls = PERSONALITIES.get(personality_name)
    if PersonalityCls is None:
        click.echo(f"Unknown personality: {personality_name}. Try one of: {', '.join(PERSONALITIES)}")
        sys.exit(2)

    # Inject an immediate startup error before constructing components
    if inject_error and inject_error.lower() == "startup":
        raise RuntimeError("Injected startup failure (requested via --inject-error=startup)")

    personality = PersonalityCls()

    # Optionally wrap the personality to throw during styling
    if inject_error and inject_error.lower() == "personality":
        class BreakingPersonality(PersonalityCls):  # type: ignore[misc]
            def style_prompt(self, user_text: str) -> str:  # type: ignore[override]
                raise RuntimeError("Injected personality failure in style_prompt")

            def style_response(self, provider_text: str) -> str:  # type: ignore[override]
                raise RuntimeError("Injected personality failure in style_response")

        personality = BreakingPersonality()

    # Choose provider based on selection
    if inject_error and inject_error.lower() == "provider":
        class FaultyProvider(LocalRulesProvider):  # type: ignore[misc]
            def generate(self, prompt: str) -> str:  # type: ignore[override]
                raise RuntimeError("Injected provider failure in generate")
        provider = FaultyProvider()
    else:
        if provider_name == "local":
            provider = LocalRulesProvider()
        elif provider_name in ["huggingface", "huggingface-chat"] and HF_AVAILABLE:
            if provider_name == "huggingface":
                click.echo(f"🤖 Loading Hugging Face model: {model_name}")
                provider = HuggingFaceProvider(model_name=model_name)
            else:
                click.echo(f"🤖 Loading Hugging Face chat model: {model_name}")
                provider = HuggingFaceChatProvider(model_name=model_name)
        elif provider_name in ["huggingface", "huggingface-chat"] and not HF_AVAILABLE:
            click.echo(f"{Fore.YELLOW}HuggingFace providers not available. Install torch/transformers to use AI models.{Style.RESET_ALL}")
            click.echo(f"Using local rules provider instead.")
            provider = LocalRulesProvider()
        else:
            click.echo(f"Unknown provider: {provider_name}. Using local rules.")
            provider = LocalRulesProvider()
    engine = Engine(provider=provider, personality=personality)

    # Initialize conversation history
    history = ConversationHistory()

    # Enhanced welcome message
    click.echo(f"\n{Fore.GREEN}╔══════════════════════════════════════╗{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}║          AI Vibe Chat 🌀              ║{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}╚══════════════════════════════════════╝{Style.RESET_ALL}")
    click.echo(f"Personality: {Fore.MAGENTA}{personality.name}{Style.RESET_ALL}")
    click.echo(f"Provider: {Fore.CYAN}{provider.name}{Style.RESET_ALL}")
    if hasattr(provider, 'model_name'):
        click.echo(f"Model: {Fore.BLUE}{provider.model_name}{Style.RESET_ALL}")
    click.echo(f"Type {Fore.CYAN}/help{Style.RESET_ALL} for commands or {Fore.CYAN}quit{Style.RESET_ALL} to exit.\n")

    while True:
        try:
            user_input = click.prompt("You", prompt_suffix=": ")
        except (EOFError, KeyboardInterrupt):
            click.echo(f"\n{Fore.GREEN}Bye! 👋{Style.RESET_ALL}")
            break

        if user_input.strip().lower() in {"quit", "exit"}:
            click.echo(f"{Fore.GREEN}Bye! 👋{Style.RESET_ALL}")
            break

        # Process commands first
        if user_input.strip().startswith("/"):
            if _process_command(user_input, history):
                continue

        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        history.add_message("You", user_input, timestamp)
        _print_user(user_input, timestamp)

        # Show typing indicator
        _show_typing_indicator()

        # Optionally error after engine produces a reply
        if inject_error and inject_error.lower() == "response":
            _ = engine.respond(user_input)
            raise RuntimeError("Injected response failure after generation")

        reply = engine.respond(user_input)
        
        # Add bot response to history
        history.add_message(personality.name, reply, timestamp)
        _print_bot(personality.name, reply, timestamp)


if __name__ == "__main__":
    main()


