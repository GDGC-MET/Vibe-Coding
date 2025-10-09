from __future__ import annotations

import sys
from typing import Dict, Type
import os
import ctypes
import contextlib

import click
from colorama import Fore, Style, init as colorama_init

from .engine import Engine
from .personalities import RizzPersonality, SarcasticPersonality
from .providers import LocalRulesProvider
import speech_recognition as sr
import pyttsx3

recognizer = sr.Recognizer()
engineSpeech= pyttsx3.init()
engineSpeech.setProperty('rate', 225)     # setting up new voice rate
engineSpeech.setProperty('volume',1.0)        # setting up volume level  between 0 and 1


PERSONALITIES: Dict[str, Type] = {
    "rizz": RizzPersonality,
    "sarcastic": SarcasticPersonality,
}

@contextlib.contextmanager
def suppress_alsa_errors():
    # Suppress ALSA warnings from the text to speech functional part
    sys.stderr = open(os.devnull, 'w')                #################
    devnull = os.open(os.devnull, os.O_WRONLY)                #
    original_stderr_fd = os.dup(2)                    #This part from AI
    ctypes.CDLL(None).fflush(None)                            #
    os.dup2(devnull, 2)                                       #
    try:                                                      #
        yield                                                 #
    finally:                                                  #
        os.dup2(original_stderr_fd, 2)                        #
        os.close(devnull)                             #################

def _print_user(text: str) -> None:
    click.echo(Fore.CYAN + "You:" + Style.RESET_ALL + f" {text}")


def _print_bot(name: str, text: str) -> None:
    click.echo(Fore.MAGENTA + f"{name}:" + Style.RESET_ALL + f" {text}")


def _speak_bot(ipstr : str):
    engineSpeech.say(ipstr)
    engineSpeech.runAndWait()


# this function from AI
def parse_key_value(ctx, param, value):
    result = {}
    if value:
        for item in value:
            if '=' in item:
                key, val = item.split('=', 1)
                result[key] = val
            else:
                raise click.BadParameter(f"Invalid format: '{item}'. Use key=value.")
    return result


def setGenderSpeech(speak):
    voices = engineSpeech.getProperty('voices')
    if speak.get('gender') == 'male':
        engineSpeech.setProperty('voice', "en+m4")
    else:
        engineSpeech.setProperty('voice', "en+f3")


@click.command()
@click.option("--personality", "personality_name", default="rizz", show_default=True)
@click.option("--speak", multiple=True  , callback=parse_key_value)
@click.option(
    "--inject-error",
    "inject_error",
    type=click.Choice(["startup", "personality", "provider", "response"], case_sensitive=False),
    default=None,
    help="Inject a controlled error for testing: startup | personality | provider | response",
)

def main(personality_name: str, speak, inject_error: str | None = None) -> None:
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

    if speak:
        while True:
            setGenderSpeech(speak)
            with suppress_alsa_errors():
                with sr.Microphone() as source:
                    _print_bot(personality.name, "Listening...")
                    audio = recognizer.listen(source)

                    # Convert speech to text
                    try:
                        user_input = recognizer.recognize_google(audio)
                        _print_user(f"{user_input}")

                    except sr.UnknownValueError:
                        _print_bot(personality.name, "Sorry, I couldn't understand.")
                        _speak_bot("Sorry, I couldn't understand.")
                        continue

                    if user_input.strip().lower() in {"quit", "exit"}:
                        click.echo("Bye!")
                        _speak_bot("Bye!")
                        break
                    # Optionally error after engineSpeech produces a reply
                    if inject_error and inject_error.lower() == "response":
                        _ = engine.respond(user_input)
                        raise RuntimeError("Injected response failure after generation")

                    reply = engine.respond(user_input)
                    _print_bot(personality.name, reply)
                    _speak_bot(reply)

    else:
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


