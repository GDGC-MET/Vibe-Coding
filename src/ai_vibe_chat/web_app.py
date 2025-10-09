from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Type

from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename

from .engine import Engine
from .personalities import RizzPersonality, SarcasticPersonality
from .providers import LocalRulesProvider, HuggingFaceProvider, HuggingFaceChatProvider


PERSONALITIES: Dict[str, Type] = {
    "rizz": RizzPersonality,
    "sarcastic": SarcasticPersonality,
}

# Configure Flask to find templates in the project root
import os
from pathlib import Path

# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent
template_dir = project_root / 'templates'

app = Flask(__name__, template_folder=str(template_dir))
app.secret_key = 'ai-vibe-chat-secret-key-2024'

# Global conversation storage (in production, use a database)
conversations: Dict[str, List[Dict]] = {}


class WebConversationHistory:
    def __init__(self, session_id: str):
        self.session_id = session_id
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
    
    def get_messages(self):
        return self.messages


def get_or_create_conversation(session_id: str) -> WebConversationHistory:
    """Get existing conversation or create new one"""
    if session_id not in conversations:
        conversations[session_id] = []
    return WebConversationHistory(session_id)


@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    personality_name = data.get('personality', 'rizz')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get or create conversation
    conversation = get_or_create_conversation(session_id)
    
    # Handle special commands
    if user_message.startswith('/'):
        return handle_command(user_message, conversation, session_id)
    
    # Get provider selection from request
    provider_name = data.get('provider', 'local')
    model_name = data.get('model', 'distilgpt2')
    
    # Create engine with selected personality and provider
    PersonalityCls = PERSONALITIES.get(personality_name, RizzPersonality)
    personality = PersonalityCls()
    
    # Choose AI provider with comprehensive error handling
    provider = None
    try:
        if provider_name == "huggingface":
            provider = HuggingFaceProvider(model_name=model_name)
        elif provider_name == "huggingface-chat":
            provider = HuggingFaceChatProvider(model_name=model_name)
        else:
            # Default to DialoGPT if unknown provider
            provider = HuggingFaceProvider(model_name=model_name)
    except Exception as e:
        # If AI provider fails, try with default model
        print(f"⚠️ AI provider failed: {e}")
        print("🔄 Trying with default model...")
        try:
            provider = HuggingFaceProvider(model_name="distilgpt2")
        except Exception as e2:
            print(f"⚠️ Default model also failed: {e2}")
            print("🔄 Using contextual AI responses...")
            # Create a minimal provider that uses contextual responses
            try:
                provider = HuggingFaceProvider(model_name="microsoft/DialoGPT-small")
                provider.use_fallback = True
            except Exception as e3:
                print(f"⚠️ All AI providers failed: {e3}")
                print("🔄 Using basic contextual responses...")
                # Create a simple provider that just returns contextual responses
                from ai_vibe_chat.providers.base import BaseProvider
                
                class ContextualProvider(BaseProvider):
                    name = "contextual"
                    
                    def generate(self, prompt: str) -> str:
                        prompt_lower = prompt.lower()
                        if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
                            return "Hello! How are you doing today?"
                        elif any(word in prompt_lower for word in ["how are you", "how are u"]):
                            return "I'm doing great, thanks for asking!"
                        elif any(word in prompt_lower for word in ["prime", "minister", "politics"]):
                            return "That's an interesting political question! What do you think about current events?"
                        else:
                            return "That's really interesting! Tell me more about that."
                
                provider = ContextualProvider()
    
    # Ensure we have a provider
    if provider is None:
        print("⚠️ No provider available, using basic contextual responses")
        from ai_vibe_chat.providers.base import BaseProvider
        
        class BasicProvider(BaseProvider):
            name = "basic"
            
            def generate(self, prompt: str) -> str:
                return "I'm here to chat! What would you like to talk about?"
        
        provider = BasicProvider()
    
    engine = Engine(provider=provider, personality=personality)
    
    # Add user message to conversation
    timestamp = datetime.now().strftime("%H:%M:%S")
    conversation.add_message("You", user_message, timestamp)
    
    # Generate bot response with error handling
    try:
        reply = engine.respond(user_message)
        if not reply or reply.strip() == "":
            reply = "I'm here and ready to chat! What would you like to talk about?"
    except Exception as e:
        print(f"⚠️ Error generating response: {e}")
        reply = "I'm having trouble thinking right now, but I'm here to chat! What's on your mind?"
    
    conversation.add_message(personality.name, reply, timestamp)
    
    # Store conversation
    conversations[session_id] = conversation.get_messages()
    
    return jsonify({
        'user_message': user_message,
        'bot_response': reply,
        'personality': personality.name,
        'timestamp': timestamp,
        'conversation': conversation.get_messages()
    })


def handle_command(command: str, conversation: WebConversationHistory, session_id: str):
    """Handle special commands"""
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == "/help":
        help_text = """
Available Commands:
• /help - Show this help message
• /clear - Clear conversation history
• /save <filename> - Save conversation to file
• /load <filename> - Load conversation from file
• /personalities - List available personalities
        """.strip()
        return jsonify({
            'command': 'help',
            'response': help_text,
            'conversation': conversation.get_messages()
        })
    
    elif cmd == "/clear":
        conversation.clear()
        conversations[session_id] = []
        return jsonify({
            'command': 'clear',
            'response': 'Conversation history cleared!',
            'conversation': []
        })
    
    elif cmd == "/save":
        if len(parts) < 2:
            return jsonify({
                'command': 'save',
                'response': 'Usage: /save <filename>',
                'conversation': conversation.get_messages()
            })
        filename = secure_filename(parts[1])
        try:
            # Create saved_conversations directory in project root
            saved_dir = project_root / 'saved_conversations'
            saved_dir.mkdir(exist_ok=True)
            with open(saved_dir / f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(conversation.get_messages(), f, indent=2, ensure_ascii=False)
            return jsonify({
                'command': 'save',
                'response': f'Conversation saved to {filename}.json!',
                'conversation': conversation.get_messages()
            })
        except Exception as e:
            return jsonify({
                'command': 'save',
                'response': f'Failed to save: {str(e)}',
                'conversation': conversation.get_messages()
            })
    
    elif cmd == "/load":
        if len(parts) < 2:
            return jsonify({
                'command': 'load',
                'response': 'Usage: /load <filename>',
                'conversation': conversation.get_messages()
            })
        filename = secure_filename(parts[1])
        try:
            saved_dir = project_root / 'saved_conversations'
            with open(saved_dir / f"{filename}.json", 'r', encoding='utf-8') as f:
                loaded_messages = json.load(f)
            conversation.messages = loaded_messages
            conversations[session_id] = loaded_messages
            return jsonify({
                'command': 'load',
                'response': f'Conversation loaded from {filename}.json!',
                'conversation': loaded_messages
            })
        except Exception as e:
            return jsonify({
                'command': 'load',
                'response': f'Failed to load: {str(e)}',
                'conversation': conversation.get_messages()
            })
    
    elif cmd == "/personalities":
        personalities_list = list(PERSONALITIES.keys())
        return jsonify({
            'command': 'personalities',
            'response': f'Available personalities: {", ".join(personalities_list)}',
            'conversation': conversation.get_messages()
        })
    
    else:
        return jsonify({
            'command': 'unknown',
            'response': f'Unknown command: {cmd}. Type /help for available commands.',
            'conversation': conversation.get_messages()
        })


@app.route('/api/personalities')
def get_personalities():
    """Get available personalities"""
    return jsonify({
        'personalities': list(PERSONALITIES.keys()),
        'default': 'rizz'
    })


@app.route('/api/conversation/<session_id>')
def get_conversation(session_id: str):
    """Get conversation for a session"""
    if session_id in conversations:
        return jsonify({'conversation': conversations[session_id]})
    return jsonify({'conversation': []})


if __name__ == '__main__':
    # Create saved_conversations directory
    os.makedirs('saved_conversations', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
