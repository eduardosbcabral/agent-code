"""Conversation history manager for Agent Code."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from rich.console import Console
from ui.display import display_info, display_error

console = Console()


class ConversationHistory:
    """Manages conversation history with context limits and pruning."""
    
    def __init__(self, max_messages: int = 50, max_total_chars: int = 100000):
        """Initialize conversation history manager."""
        self.messages: List[Dict[str, Any]] = []
        self.max_messages = max_messages
        self.max_total_chars = max_total_chars
        
    def add_system_message(self, content: str, meta_prompt: str = None):
        """Add the initial system message with meta-prompt."""
        # Clear any existing system messages
        self.messages = [msg for msg in self.messages if msg.get('role') != 'system']
        
        # Add new system message at the beginning
        system_content = meta_prompt if meta_prompt else content
        self.messages.insert(0, {
            'role': 'system',
            'content': system_content,
            'timestamp': datetime.now().isoformat(),
            'type': 'system'
        })
        
        display_info("System message added to conversation history")
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append({
            'role': 'user',
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'type': 'user_input'
        })
        
        self._prune_if_needed()
        # display_info(f"User message added (total messages: {len(self.messages)})")
    
    def add_assistant_response(self, thoughts: str, final_text: str, actions: List[Dict] = None):
        """Add an assistant response with thoughts and actions."""
        self.messages.append({
            'role': 'assistant',
            'content': final_text,
            'thoughts': thoughts,
            'actions': actions or [],
            'timestamp': datetime.now().isoformat(),
            'type': 'assistant_response'
        })
        
        self._prune_if_needed()
        # display_info(f"Assistant response added (total messages: {len(self.messages)})")
    
    def add_observation(self, observations: str):
        """Add system observations from tool execution."""
        self.messages.append({
            'role': 'user',  # Observations are treated as user input to the AI
            'content': f"SYSTEM OBSERVATIONS:\n{observations}",
            'timestamp': datetime.now().isoformat(),
            'type': 'system_observation'
        })
        
        self._prune_if_needed()
        #display_info("System observations added to conversation")
    
    def get_conversation_for_api(self) -> List[Dict[str, Any]]:
        """Get conversation formatted for API calls."""
        api_messages = []
        
        for message in self.messages:
            api_message = {
                'role': message['role'],
                'content': message['content']
            }
            api_messages.append(api_message)
        
        return api_messages
    
    def get_total_char_count(self) -> int:
        """Get total character count of all messages."""
        total = 0
        for message in self.messages:
            total += len(message.get('content', ''))
            if 'thoughts' in message:
                total += len(message['thoughts'])
        return total
    
    def _prune_if_needed(self):
        """Prune conversation if it exceeds limits."""
        # Check message count limit
        if len(self.messages) > self.max_messages:
            self._prune_by_message_count()
        
        # Check character count limit
        if self.get_total_char_count() > self.max_total_chars:
            self._prune_by_char_count()
    
    def _prune_by_message_count(self):
        """Prune by removing oldest non-system messages."""
        # Keep system message and recent messages
        system_messages = [msg for msg in self.messages if msg.get('role') == 'system']
        other_messages = [msg for msg in self.messages if msg.get('role') != 'system']
        
        # Keep only the most recent messages
        keep_count = self.max_messages - len(system_messages)
        if keep_count > 0:
            other_messages = other_messages[-keep_count:]
        else:
            other_messages = []
        
        self.messages = system_messages + other_messages
        # display_info(f"Pruned conversation by message count to {len(self.messages)} messages")
    
    def _prune_by_char_count(self):
        """Prune by removing messages until under character limit."""
        # Always keep system messages
        system_messages = [msg for msg in self.messages if msg.get('role') == 'system']
        other_messages = [msg for msg in self.messages if msg.get('role') != 'system']
        
        # Remove oldest messages until under limit
        while other_messages and self.get_total_char_count() > self.max_total_chars:
            other_messages.pop(0)
        
        self.messages = system_messages + other_messages
        # display_info(f"Pruned conversation by character count to {self.get_total_char_count()} chars")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation history."""
        message_types = {}
        for message in self.messages:
            msg_type = message.get('type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        return {
            'total_messages': len(self.messages),
            'total_characters': self.get_total_char_count(),
            'message_types': message_types,
            'oldest_message': self.messages[1]['timestamp'] if len(self.messages) > 1 else None,
            'newest_message': self.messages[-1]['timestamp'] if self.messages else None
        }
    
    def clear(self):
        """Clear all conversation history."""
        self.messages = []
        display_info("Conversation history cleared")
    
    def export_to_json(self) -> str:
        """Export conversation history to JSON string."""
        return json.dumps(self.messages, indent=2, default=str)
