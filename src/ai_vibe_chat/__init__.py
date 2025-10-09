''' #Issue BOT-VIBE-001: Bot responds too formally, ignoring selected "vibe"

## DescriptionWhen users choose a specific "vibe" (e.g., casual, friendly, sarcastic), the bot often defaults to a neutral or overly formal tone.

## Steps to Reproduce 1.select "casual" vibe from settings 2. ask a basic question like "what's the whether ?" 3. Bot replies in a robotic/formal tone 

## Expected Behaviorot should respond in a casual tone, matching the selected vibe/personality.

## Possible CausePersonality prompt may be overwritten or not injected properly into the prompt template. vibe state may not persist across miltiple turns

## Suggested FixEnsure selected vibe is embedded in the prompt generation pipeline. use presistent user session 
'''

__all__ = [
    "engine",
    "personalities",
    "providers",
]


