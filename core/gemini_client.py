"""Gemini API client wrapper for Chapter Agent."""

import asyncio
from typing import List, Dict, Any, Optional
import google.genai as genai
from google.genai import types

from rich.console import Console
from config.settings import Config
from ui.display import display_error, display_info

console = Console()


class GeminiClient:
    """Async wrapper for Google Gemini API client."""
    
    def __init__(self, config: Config):
        """Initialize the Gemini client."""
        self.config = config
        self.client = None
        self.model_name = "gemini-2.5-flash"
        
    async def initialize(self):
        """Initialize the async Gemini client."""
        try:
            self.client = genai.Client(api_key=self.config.gemini_api_key)
            display_info("Gemini client initialized successfully")
            return True
        except Exception as e:
            display_error(f"Failed to initialize Gemini client: {e}")
            return False
    
    async def generate_response(
        self, 
        conversation_history: List[Dict[str, Any]],
        enable_thinking: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Generate a response from the Gemini model."""
        try:
            if not self.client:
                await self.initialize()
            
            # Prepare the conversation for Gemini
            contents = self._prepare_contents(conversation_history)
            
            # Generate response with thinking enabled
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Lower temperature for more consistent responses
                    max_output_tokens=4096
                )
            )
            
            # Extract response data
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # Extract thinking and final content
                thoughts, final_text = self._extract_thoughts_and_text(candidate.content)
                
                return {
                    'thoughts': thoughts,
                    'final_text': final_text,
                    'finish_reason': candidate.finish_reason,
                    'safety_ratings': candidate.safety_ratings
                }
            else:
                display_error("No response candidates received from Gemini")
                return None
                
        except Exception as e:
            display_error(f"Error generating response: {e}")
            return None
    
    def _prepare_contents(self, conversation_history: List[Dict[str, Any]]) -> List[types.Content]:
        """Convert conversation history to Gemini Content format."""
        contents = []
        
        for message in conversation_history:
            role = message.get('role', 'user')
            text = message.get('content', '')
            
            # Map roles to Gemini format
            if role == 'system':
                role = 'user'  # Gemini treats system messages as user messages
            elif role == 'assistant':
                role = 'model'
            
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=text)]
            ))
        
        return contents
    
    def _extract_thoughts_and_text(self, content: types.Content) -> tuple[str, str]:
        """Extract thinking and final text from response content."""
        thoughts = ""
        final_text = ""
        
        if content.parts:
            for part in content.parts:
                if hasattr(part, 'thought') and part.thought:
                    thoughts += part.text + "\n"
                else:
                    final_text += part.text + "\n"
        
        # If no separate thinking found, use the full text as final
        if not thoughts and final_text:
            thoughts = "[No separate thinking provided]"
        
        return thoughts.strip(), final_text.strip()
    
    async def test_connection(self) -> bool:
        """Test the connection to Gemini API."""
        try:
            if not self.client:
                await self.initialize()
            
            # Simple test request
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role='user',
                    parts=[types.Part(text="Hello, respond with 'Connection successful'")]
                )]
            )
            
            if response.candidates and len(response.candidates) > 0:
                text = response.candidates[0].content.parts[0].text
                if "Connection successful" in text:
                    display_info("✓ Gemini API connection test successful")
                    return True
            
            display_error("Gemini API connection test failed")
            return False
            
        except Exception as e:
            display_error(f"Gemini API connection test failed: {e}")
            return False
