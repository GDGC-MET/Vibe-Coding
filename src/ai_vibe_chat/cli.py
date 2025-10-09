from __future__ import annotations

import sys
from typing import Dict, Type

import click
from colorama import Fore, Style, init as colorama_init
from dotenv import load_dotenv

from .data_model import ConversationTurn
from .engine import Engine, Provider
from .personalities import RizzPersonality, SarcasticPersonality
from .providers import LocalRulesProvider
from .providers.perplexity import PerplexityProvider
from .providers.gemini import GeminiProvider


PERSONALITIES: Dict[str, Type] = {
    "rizz": RizzPersonality,
    "sarcastic": SarcasticPersonality,
}

PROVIDERS: Dict[str, Type[Provider]] = {
    "local-rules": LocalRulesProvider,
    "perplexity": PerplexityProvider,
    "gemini": GeminiProvider,
}


def _print_user(text: str) -> None:
    click.echo(Fore.CYAN + "You:" + Style.RESET_ALL + f" {text}")


def _print_bot(name: str, text: str) -> None:
    click.echo(Fore.MAGENTA + f"{name}:" + Style.RESET_ALL + f" {text}")


@click.command()
@click.option("--personality", "personality_name", default="rizz", show_default=True)
@click.option("--provider", "provider_name", default="local-rules", show_default=True, type=click.Choice(list(PROVIDERS.keys())))
@click.option(
    "--inject-error",
    "inject_error",
    type=click.Choice(["startup", "personality", "provider", "response"], case_sensitive=False),
    default=None,
    help="Inject a controlled error for testing: startup | personality | provider | response",
)
@click.option("--memory", "memory", is_flag=True, default=False, help="Enable conversation memory.")
def main(personality_name: str, provider_name: str, inject_error: str | None = None, memory: bool = False) -> None:
    """CLI entrypoint for AI Vibe Chat.

    Validates options, constructs the Engine, and runs a simple REPL.
    """
    load_dotenv()
    colorama_init(autoreset=True)

    PersonalityCls = PERSONALITIES.get(personality_name)
    if PersonalityCls is None:
        click.echo(f"Unknown personality: {personality_name}. Try one of: {', '.join(PERSONALITIES)}")
        sys.exit(2)

    ProviderCls = PROVIDERS.get(provider_name)
    if ProviderCls is None:
        click.echo(f"Unknown provider: {provider_name}. Try one of: {', '.join(PROVIDERS)}")
        sys.exit(2)

    # There are no conflicting flags currently; enforce simple invariants here if needed
    if inject_error is not None and inject_error.lower() not in {"startup", "personality", "provider", "response"}:
        click.echo("Invalid --inject-error option")
        sys.exit(2)

    # Inject an immediate startup error before constructing components
    if inject_error and inject_error.lower() == "startup":
        raise RuntimeError("Injected startup failure (requested via --inject-error=startup)")

    personality = PersonalityCls()

    # Optionally wrap the personality to throw during styling
    if inject_error and inject_error.lower() == "personality":
        class BreakingPersonality(PersonalityCls):  # type: ignore[misc, valid-type]
            def style_prompt(self, user_text: str) -> str:  # type: ignore[override]
                raise RuntimeError("Injected personality failure in style_prompt")

            def style_response(self, provider_text: str) -> str:  # type: ignore[override]
                raise RuntimeError("Injected personality failure in style_response")

        personality = BreakingPersonality()

    # Choose provider; optionally make it faulty
    provider: Provider
    if inject_error and inject_error.lower() == "provider":
        class FaultyProvider(LocalRulesProvider):  # type: ignore[misc]
            def generate(self, prompt: str, history: list[ConversationTurn] | None = None) -> str:  # type: ignore[override]
                raise RuntimeError("Injected provider failure in generate")

        provider = FaultyProvider()
    else:
        try:
            provider = ProviderCls()
        except ValueError as e:
            click.echo(f"Error initializing provider: {e}", err=True)
            sys.exit(1)

    engine = Engine(provider=provider, personality=personality, memory=memory)

    click.echo(Fore.GREEN + "AI Vibe Chat 🌀" + Style.RESET_ALL)
    click.echo(f"Personality: {personality.name}")
    click.echo(f"Provider: {provider.name}")
    if memory:
        click.echo("Memory: " + Fore.GREEN + "ON" + Style.RESET_ALL)
    click.echo("Type 'quit' to exit.\n")

    while True:
        try:
            user_input = click.prompt("You")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break

        if user_input.strip().lower() in {"quit", "exit"}:
            click.echo("Bye!")
            break

        _print_user(user_input)
        # Optionally error after engine produces a reply
        if inject_error and inject_error.lower() == "response":
            _ = engine.respond(user_input)
            raise RuntimeError("Injected response failure after generation")

        reply = engine.respond(user_input)
        _print_bot(personality.name, reply)


if __name__ == "__main__":
    main()


