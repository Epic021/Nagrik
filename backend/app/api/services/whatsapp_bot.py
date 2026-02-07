"""
WhatsApp Bot Service - Gemini AI Chat Integration

This module handles:
1. Conversation management for WhatsApp users
2. Gemini AI integration for chat responses
3. Image analysis for complaints
"""

import os
import traceback
from typing import Optional, Dict, List, Any
import google.generativeai as genai
from ..core.config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# System prompt for complaint registration
SYSTEM_PROMPT = """You are a helpful customer service assistant for NAGRIK - Delhi's civic grievance platform.

Your job is to:
1. Greet the user and ask for their complaint details
2. Collect: Name, Contact, Complaint Category, Description
3. If they send an image, analyze it and include relevant details
4. Once all info is collected, summarize the complaint
5. Route to appropriate department based on category

Categories:
- Potholes & Road Damage → PWD (Public Works Department)
- Garbage & Sanitation → MCD Sanitation
- Street Lights → Electrical Department
- Water Supply Issues → Delhi Jal Board
- Illegal Construction → Building Department
- Traffic Issues → Traffic Police
- Noise Pollution → Pollution Control
- Other → General Support

Be concise, professional, and helpful. Ask one question at a time.
Always respond in a friendly manner and acknowledge the user's concerns."""

# Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')


class WhatsAppConversationManager:
    """Manages conversation history for WhatsApp users."""
    
    def __init__(self, max_history: int = 10):
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history
    
    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a user."""
        return self.conversations.get(user_id, [])
    
    def add_turn(self, user_id: str, user_message: str, assistant_response: str):
        """Add a conversation turn to history."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            'user': user_message,
            'assistant': assistant_response
        })
        
        # Keep only last N turns
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]
    
    def clear(self, user_id: str) -> bool:
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
            return True
        return False
    
    def has_session(self, user_id: str) -> bool:
        """Check if user has an active session."""
        return user_id in self.conversations


# Global conversation manager instance
conversation_manager = WhatsAppConversationManager()


async def generate_chat_response(
    user_id: str,
    message: str = "",
    image_base64: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a chat response using Gemini AI.
    
    Args:
        user_id: Unique identifier for the WhatsApp user
        message: Text message from user
        image_base64: Optional base64 encoded image
        
    Returns:
        Dict with 'response' text and 'success' boolean
    """
    try:
        if not message and not image_base64:
            return {'response': '', 'success': False, 'error': 'No message or image provided'}
        
        # Initialize conversation if new user
        if not conversation_manager.has_session(user_id):
            conversation_manager.conversations[user_id] = []
        
        # Build conversation context
        history = conversation_manager.get_history(user_id)
        history_text = ""
        for turn in history:
            history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"
        
        # Create the full prompt
        full_prompt = f"""{SYSTEM_PROMPT}

Previous conversation:
{history_text if history_text else "(No previous conversation)"}

User's current message: {message if message else "(sent an image)"}

Please respond helpfully:"""

        # Generate response with or without image
        if image_base64:
            response = model.generate_content([
                full_prompt,
                {
                    'mime_type': 'image/jpeg',
                    'data': image_base64
                }
            ])
        else:
            response = model.generate_content(full_prompt)
        
        response_text = response.text
        
        # Store in history
        conversation_manager.add_turn(
            user_id,
            message if message else '[image]',
            response_text
        )
        
        return {
            'response': response_text,
            'success': True
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            'response': '',
            'success': False,
            'error': str(e)
        }


async def clear_session(user_id: str) -> Dict[str, Any]:
    """
    Clear conversation session for a user.
    
    Args:
        user_id: Unique identifier for the WhatsApp user
        
    Returns:
        Dict with 'success' boolean and 'message'
    """
    cleared = conversation_manager.clear(user_id)
    if cleared:
        return {'success': True, 'message': 'Session cleared'}
    return {'success': True, 'message': 'No session found'}


def get_active_sessions_count() -> int:
    """Get count of active conversation sessions."""
    return len(conversation_manager.conversations)
