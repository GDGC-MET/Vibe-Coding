#  src/ai_vibe_chat/typing_indicator.py

import sys
import time
def typing_indicator(duration: float = 1.5, bot_name: str = "bot"):
  """
  Displays a simple typing indicator in the terminal.

  Args:
      duration (float): Total time (in seconds) for the animation.
      bot_name (str): The name of the bot/personality.
  """
  print(f"{bot_name} is typing",end="", flush=True)
  steps = 3
  delay = duration / steps

  for _ in range(steps):
    time.sleep(delay)
    print(".", end="", flush=True)
    print() # move to next line after typing
