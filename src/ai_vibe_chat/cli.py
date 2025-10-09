from __future__ import annotations

from .personalities.wholesome import WholesomePersonality
from ai_vibe_chat.personalities.wholesome import WholesomePersonality

import sys
from typing import Dict, Type

import click
from colorama import Fore, Style, init as colorama_init

from .engine import Engine
from .personalities import RizzPersonality, SarcasticPersonality
from .providers import LocalRulesProvider


PERSONALITIES: Dict[str, Type] = {
    "wholesome": WholesomePersonality,
    "rizz": RizzPersonality,
    "sarcastic": SarcasticPersonality,
}


def _print_user(text: str) -> None:
    click.echo(Fore.CYAN + "You:" + Style.RESET_ALL + f" {text}")


def _print_bot(name: str, text: str) -> None:
    click.echo(Fore.MAGENTA + f"{name}:" + Style.RESET_ALL + f" {text}")


@click.command()
@click.option("--personality", "personality_name", default="rizz", show_default=True)
@click.option(
    "--inject-error",
    "inject_error",
    type=click.Choice(["startup", "personality", "provider", "response"], case_sensitive=False),
    default=None,
    help="Inject a controlled error for testing: startup | personality | provider | response",
)
def main(personality_name: str, inject_error: str | None = None) -> None:
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

    # Choose provider; optionally make it faulty
    if inject_error and inject_error.lower() == "provider":
        class FaultyProvider(LocalRulesProvider):  # type: ignore[misc]
            def generate(self, prompt: str) -> str:  # type: ignore[override]
                raise RuntimeError("Injected provider failure in generate")

        provider = FaultyProvider()
    else:
        provider = LocalRulesProvider()
    engine = Engine(provider=provider, personality=personality)

    click.echo(Fore.GREEN + "AI Vibe Chat 🌀" + Style.RESET_ALL)
    click.echo(f"Personality: {personality.name}\nType 'quit' to exit.\n")

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


