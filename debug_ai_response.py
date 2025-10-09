#!/usr/bin/env python3
"""
Debug AI response generation to find the issue.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_vibe_chat.providers.huggingface_provider import HuggingFaceProvider
from ai_vibe_chat.personalities import RizzPersonality
from ai_vibe_chat.engine import Engine

def debug_ai_response():
    print("🔍 Debugging AI Response Generation...")
    
    try:
        # Initialize provider
        provider = HuggingFaceProvider(model_name="microsoft/DialoGPT-small")
        personality = RizzPersonality()
        engine = Engine(provider=provider, personality=personality)
        
        print(f"Provider: {provider.name}")
        print(f"Use fallback: {getattr(provider, 'use_fallback', False)}")
        print(f"Personality: {personality.name}")
        
        # Test simple message
        test_message = "hi"
        print(f"\n📝 Testing message: '{test_message}'")
        
        # Check conversation history
        print(f"Conversation history: {provider.conversation_history}")
        
        # Generate response
        print("Generating response...")
        response = provider.generate(test_message)
        print(f"Raw AI response: '{response}'")
        
        # Apply personality styling
        styled_response = personality.style_response(response)
        print(f"Styled response: '{styled_response}'")
        
        # Test engine response
        engine_response = engine.respond(test_message)
        print(f"Engine response: '{engine_response}'")
        
        # Check conversation history after
        print(f"Conversation history after: {provider.conversation_history}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = debug_ai_response()
    if success:
        print("✅ Debug completed!")
    else:
        print("❌ Debug failed!")
