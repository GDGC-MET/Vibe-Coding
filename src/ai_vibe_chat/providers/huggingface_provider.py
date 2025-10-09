from __future__ import annotations

import torch
from typing import List, Dict, Optional
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline,
    set_seed
)
import warnings

from .base import BaseProvider


class HuggingFaceProvider(BaseProvider):
    name = "huggingface"
    
    def __init__(self, model_name: str = "distilgpt2", device: str = "auto"):
        """
        Initialize Hugging Face provider with a conversational model.
        
        Args:
            model_name: Hugging Face model name (e.g., "microsoft/DialoGPT-medium", "facebook/blenderbot-400M-distill")
            device: Device to run on ("auto", "cpu", "cuda")
        """
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.conversation_history: List[Dict[str, str]] = []
        
        # Suppress warnings for cleaner output
        warnings.filterwarnings("ignore", category=UserWarning)
        
        print(f"🤖 Loading {model_name} on {self.device}...")
        
        try:
            # Load tokenizer and model with better settings for large models
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            # Move model to device if not using device_map
            if self.device != "cuda" or "device_map" not in str(self.model):
                self.model = self.model.to(self.device)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline with optimized settings
            self.conversation_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            print(f"✅ {model_name} loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading {model_name}: {e}")
            print("🔄 Will use contextual AI responses instead of fallback")
            self.use_fallback = True
            return
        
        self.use_fallback = False
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using Hugging Face model.
        
        Args:
            prompt: User input prompt
            
        Returns:
            Generated response
        """
        if self.use_fallback:
            return self.fallback_provider.generate(prompt)
        
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Try AI generation first, but with better fallback
            ai_response = None
            try:
                # Create conversation context
                conversation_text = self._create_conversation_context()
                
                # Generate response with strict parameters for short, focused responses
                response = self.conversation_pipeline(
                    conversation_text,
                    max_new_tokens=20,
                    num_return_sequences=1,
                    temperature=0.5,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    truncation=True,
                    repetition_penalty=1.5,
                    top_p=0.8,
                    top_k=20,
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
                
                # Extract the generated text
                generated_text = response[0]['generated_text']
                ai_response = generated_text[len(conversation_text):].strip()
                
            except Exception as e:
                print(f"⚠️ AI generation failed: {e}")
                ai_response = None
            
            # Process AI response if available
            bot_response = None
            if ai_response:
                # Clean up the response - remove AI: prefix if present
                if ai_response.startswith("AI:"):
                    bot_response = ai_response[3:].strip()
                elif ai_response.startswith("Bot:"):
                    bot_response = ai_response[4:].strip()
                else:
                    bot_response = ai_response.strip()
                
                # Remove any remaining prefixes and clean up
                bot_response = bot_response.replace("Human:", "").replace("AI:", "").replace("Bot:", "").strip()
                
                # Remove any incomplete sentences or random text
                if "Human:" in bot_response:
                    bot_response = bot_response.split("Human:")[0].strip()
                
                # Clean up rambling responses - take only first sentence
                sentences = bot_response.split('.')
                if len(sentences) > 1:
                    bot_response = sentences[0].strip() + "."
                
                # Filter out very long responses (more than 100 characters)
                if len(bot_response) > 100:
                    bot_response = bot_response[:100].strip()
                    # Find last complete word
                    last_space = bot_response.rfind(' ')
                    if last_space > 50:
                        bot_response = bot_response[:last_space] + "..."
                
                # Check if response is good quality - be more lenient to allow AI responses
                if (len(bot_response) < 2 or 
                    bot_response in ["", "I", "You", "The", "A", "An"] or
                    bot_response.startswith("AI:") or
                    bot_response.startswith("Human:") or
                    bot_response == "Tell me more."):
                    bot_response = None  # Will use fallback
            
            # If AI response is not good, try to improve it or use a default AI response
            if not bot_response:
                # Generate a more creative AI response with different parameters
                try:
                    # Try with more creative parameters
                    creative_response = self.conversation_pipeline(
                        conversation_text,
                        max_new_tokens=120,
                        temperature=1.0,
                        do_sample=True,
                        top_p=0.95,
                        top_k=100,
                        repetition_penalty=1.05,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        truncation=True
                    )
                    
                    generated_text = creative_response[0]['generated_text']
                    creative_ai_response = generated_text[len(conversation_text):].strip()
                    
                    # Clean up the creative response
                    if creative_ai_response.startswith("AI:"):
                        creative_ai_response = creative_ai_response[3:].strip()
                    elif creative_ai_response.startswith("Bot:"):
                        creative_ai_response = creative_ai_response[4:].strip()
                    
                    creative_ai_response = creative_ai_response.replace("Human:", "").replace("AI:", "").replace("Bot:", "").strip()
                    
                    if "Human:" in creative_ai_response:
                        creative_ai_response = creative_ai_response.split("Human:")[0].strip()
                    
                    if len(creative_ai_response) > 3 and len(creative_ai_response.split()) > 1:
                        bot_response = creative_ai_response
                    else:
                        # Final fallback - generate a contextual AI response
                        bot_response = self._generate_contextual_response(prompt)
                        
                except Exception as e:
                    print(f"⚠️ Creative AI generation failed: {e}")
                    bot_response = self._generate_contextual_response(prompt)
            
            # Add bot response to conversation history
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            # Limit conversation history to prevent memory issues
            if len(self.conversation_history) > 20:  # Keep last 10 exchanges
                self.conversation_history = self.conversation_history[-20:]
            
            return bot_response.strip() if bot_response.strip() else "I understand. Tell me more!"
            
        except Exception as e:
            print(f"⚠️ Error generating response: {e}")
            # Fallback to local rules
            from .local_rules import LocalRulesProvider
            fallback = LocalRulesProvider()
            return fallback.generate(prompt)
    
    def _create_conversation_context(self) -> str:
        """
        Create conversation context for text generation.
        """
        current_user_input = self.conversation_history[-1]["content"]
        
        # Simple, effective prompt for DistilGPT-2
        context = f"Human: {current_user_input}\nAI:"
        
        return context
    
    def _generate_contextual_response(self, prompt: str) -> str:
        """Generate a contextual AI response when normal generation fails"""
        prompt_lower = prompt.lower()
        
        # Generate contextual responses based on user input
        if any(word in prompt_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! How are you doing today?"
        elif any(word in prompt_lower for word in ["how are you", "how are u", "how r u"]):
            return "I'm doing great, thanks for asking! How about you?"
        elif any(word in prompt_lower for word in ["what", "who", "where", "when", "why", "how"]):
            return "That's an interesting question! Can you tell me more about what you're thinking?"
        elif any(word in prompt_lower for word in ["name", "who are you"]):
            return "I'm an AI assistant! What would you like to talk about?"
        elif any(word in prompt_lower for word in ["good", "great", "awesome", "amazing", "wonderful"]):
            return "That's wonderful to hear! I'm glad things are going well for you."
        elif any(word in prompt_lower for word in ["bad", "terrible", "awful", "sad", "upset"]):
            return "I'm sorry to hear that. Is there anything I can help you with?"
        elif any(word in prompt_lower for word in ["love", "like", "enjoy", "favorite"]):
            return "That sounds really nice! I'd love to hear more about it."
        else:
            return "That's really interesting! Tell me more about that."
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history."""
        return self.conversation_history.copy()
    
    def set_conversation_history(self, history: List[Dict[str, str]]):
        """Set conversation history."""
        self.conversation_history = history.copy()


class HuggingFaceChatProvider(BaseProvider):
    """
    Alternative provider using Hugging Face's chat models.
    """
    name = "huggingface-chat"
    
    def __init__(self, model_name: str = "distilgpt2", device: str = "auto"):
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.conversation_history: List[str] = []
        
        print(f"🤖 Loading chat model {model_name} on {self.device}...")
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move to device
            self.model = self.model.to(self.device)
            
            # Add padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print(f"✅ {model_name} loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading {model_name}: {e}")
            print("🔄 Will use contextual AI responses instead of fallback")
            self.use_fallback = True
            return
        
        self.use_fallback = False
    
    def generate(self, prompt: str) -> str:
        """Generate response using the chat model."""
        if self.use_fallback:
            return self._generate_contextual_response(prompt)
        
        try:
            # Add user input to conversation
            self.conversation_history.append(f"User: {prompt}")
            
            # Create conversation context
            conversation_text = " ".join(self.conversation_history[-10:])  # Last 10 exchanges
            conversation_text += " Bot:"
            
            # Tokenize input
            inputs = self.tokenizer.encode(conversation_text, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,  # Generate up to 50 new tokens
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            
            # Clean up response
            response = response.strip()
            if response.startswith("Bot:"):
                response = response[4:].strip()
            
            # Add bot response to conversation
            self.conversation_history.append(f"Bot: {response}")
            
            # Limit conversation history
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return response
            
        except Exception as e:
            print(f"⚠️ Error generating response: {e}")
            return self._generate_contextual_response(prompt)
    
    def _generate_contextual_response(self, prompt: str) -> str:
        """Generate a contextual AI response when normal generation fails"""
        prompt_lower = prompt.lower()
        
        # Generate contextual responses based on user input
        if any(word in prompt_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! How are you doing today?"
        elif any(word in prompt_lower for word in ["how are you", "how are u", "how r u"]):
            return "I'm doing great, thanks for asking! How about you?"
        elif any(word in prompt_lower for word in ["what", "who", "where", "when", "why", "how"]):
            return "That's an interesting question! Can you tell me more about what you're thinking?"
        elif any(word in prompt_lower for word in ["name", "who are you"]):
            return "I'm an AI assistant! What would you like to talk about?"
        elif any(word in prompt_lower for word in ["good", "great", "awesome", "amazing", "wonderful"]):
            return "That's wonderful to hear! I'm glad things are going well for you."
        elif any(word in prompt_lower for word in ["bad", "terrible", "awful", "sad", "upset"]):
            return "I'm sorry to hear that. Is there anything I can help you with?"
        elif any(word in prompt_lower for word in ["love", "like", "enjoy", "favorite"]):
            return "That sounds really nice! I'd love to hear more about it."
        else:
            return "That's really interesting! Tell me more about that."
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def get_conversation_history(self) -> List[str]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def set_conversation_history(self, history: List[str]):
        """Set conversation history."""
        self.conversation_history = history.copy()
