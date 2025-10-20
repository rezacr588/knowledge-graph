"""
Chat Service using Gemini for RAG-based Q&A
Generates contextual answers based on retrieved documents
"""

import logging
from typing import List, Optional, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for generating chat responses using Gemini with RAG context
    """
    
    def __init__(self, gemini_api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize chat service
        
        Args:
            gemini_api_key: Google Gemini API key
            model_name: Gemini model to use
        """
        try:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"✅ Chat service initialized with {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en"
    ) -> str:
        """
        Generate a chat response based on query and retrieved context
        
        Args:
            query: User's question
            retrieved_chunks: List of retrieved document chunks with text and metadata
            conversation_history: Optional previous messages for context
            language: Language code
        
        Returns:
            Generated response text
        """
        # Build context from retrieved chunks
        context = self._build_context(retrieved_chunks)
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            history_text = self._build_history(conversation_history)
        
        # Create prompt
        prompt = self._create_prompt(query, context, history_text, language)
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            logger.info(f"Generated response ({len(answer)} chars)")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "I apologize, but I encountered an error while generating a response. Please try again."
    
    def _build_context(self, retrieved_chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        if not retrieved_chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks[:5], 1):  # Limit to top 5
            text = chunk.get('text', '')
            score = chunk.get('rrf_score', 0)
            context_parts.append(f"[Context {i}] (Relevance: {score:.3f})\n{text}")
        
        return "\n\n".join(context_parts)
    
    def _build_history(self, conversation_history: List[Dict]) -> str:
        """Build conversation history string"""
        history_parts = []
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_parts.append(f"{role.upper()}: {content}")
        
        return "\n".join(history_parts)
    
    def _create_prompt(
        self,
        query: str,
        context: str,
        history: str,
        language: str
    ) -> str:
        """Create the full prompt for Gemini"""
        
        language_instructions = {
            "en": "Answer in English.",
            "es": "Responde en español.",
            "ar": "أجب باللغة العربية."
        }
        
        lang_instruction = language_instructions.get(language, "Answer in English.")
        
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context from documents.

{lang_instruction}

Rules:
1. Answer the question using ONLY the information from the context provided below
2. If the context doesn't contain enough information to answer, say so clearly
3. Be concise but comprehensive
4. Cite which context section(s) you used in your answer
5. If multiple context sections are relevant, synthesize the information
6. Maintain conversation continuity by considering previous messages

"""
        
        if history:
            prompt += f"Previous Conversation:\n{history}\n\n"
        
        prompt += f"""Context from Documents:
{context}

Current Question: {query}

Answer:"""
        
        return prompt
    
    def generate_streaming_response(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en"
    ):
        """
        Generate a streaming chat response (for future implementation)
        
        Args:
            query: User's question
            retrieved_chunks: List of retrieved document chunks
            conversation_history: Optional previous messages
            language: Language code
        
        Yields:
            Response chunks as they are generated
        """
        # Build context
        context = self._build_context(retrieved_chunks)
        history_text = ""
        if conversation_history:
            history_text = self._build_history(conversation_history)
        
        prompt = self._create_prompt(query, context, history_text, language)
        
        try:
            # Use streaming generation
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield "Error generating response."
