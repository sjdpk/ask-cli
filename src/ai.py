#!/usr/bin/env python3
"""
AI client for command generation

This module handles all interactions with the AI service for generating
terminal commands from natural language queries.
"""

import getpass
import time
from typing import Optional

# Import local modules
from config import get_os_name
from constants import (
    AI_MODEL, AI_TEMPERATURE, AI_MAX_OUTPUT_TOKENS, MAX_API_RETRIES,
    INITIAL_RETRY_DELAY, ERROR_MESSAGES
)

# Import google.generativeai with error handling
try:
    import google.generativeai as genai
except ImportError as e:
    raise ImportError("Google Generative AI package not found. Please reinstall Ask CLI.") from e


class CommandGenerator:
    """
    AI-powered command generator with comprehensive error handling.
    
    This class manages interactions with the AI service to convert natural
    language queries into appropriate terminal commands for the user's system.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the command generator with API key validation.
        
        Sets up the AI model configuration and validates the provided API key
        for secure communication with the AI service.
        
        Args:
            api_key: Valid API key for the AI service
            
        Raises:
            ValueError: If API key is empty or None
            RuntimeError: If AI model initialization fails
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key is required and cannot be empty")
            
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(AI_MODEL)
            self.os_name = get_os_name()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AI model: {str(e)}") from e
    
    def get_command_with_context(self, query: str, context) -> str:
        """
        Generate terminal command with conversation context for follow-up queries.
        
        Processes a follow-up query using conversation context to generate
        more relevant and contextually aware commands.
        
        Args:
            query: Natural language description of the desired action
            context: ConversationContext object with query history
            
        Returns:
            Generated command string or error message
            
        Side Effects:
            May print retry status messages during network issues
        """
        if not query or not query.strip():
            return "➜ Please provide a valid query"
            
        try:
            username = getpass.getuser()
            prompt = self._build_contextual_prompt(username, query, context)
            
            # Use the same generation logic as regular queries
            return self._generate_with_retries(prompt)
            
        except KeyboardInterrupt:
            return "➜ Operation cancelled by user"
        except Exception as e:
            error_str = str(e).lower()
            if "permission" in error_str:
                return "➜ Permission denied. Please check your system permissions."
            else:
                return f"➜ Unexpected error: {str(e)}"
    
    def get_command(self, query: str) -> str:
        """
        Generate terminal command from natural language query.
        
        Processes a natural language query and generates an appropriate terminal
        command using AI, with retry logic and comprehensive error handling.
        
        Args:
            query: Natural language description of the desired action
            
        Returns:
            Generated command string or error message
            
        Side Effects:
            May print retry status messages during network issues
        """
        if not query or not query.strip():
            return "➜ Please provide a valid query"
            
        try:
            username = getpass.getuser()
            prompt = self._build_prompt(username, query)
            
            # Use shared generation logic
            return self._generate_with_retries(prompt)
            
        except KeyboardInterrupt:
            return "➜ Operation cancelled by user"
        except Exception as e:
            error_str = str(e).lower()
            if "permission" in error_str:
                return "➜ Permission denied. Please check your system permissions."
            else:
                return f"➜ Unexpected error: {str(e)}"
    
    def _generate_with_retries(self, prompt: str) -> str:
        """
        Generate content with retry logic and error handling.
        
        Shared method for both regular and contextual command generation
        with comprehensive retry and error handling logic.
        
        Args:
            prompt: The formatted prompt to send to the AI
            
        Returns:
            Generated response or error message
        """
        retry_delay = INITIAL_RETRY_DELAY
        
        for attempt in range(MAX_API_RETRIES):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=AI_TEMPERATURE,
                        max_output_tokens=AI_MAX_OUTPUT_TOKENS
                    )
                )
                
                if response and response.text:
                    return response.text.strip()
                else:
                    return "➜ AI service returned empty response. Please try again."
                    
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle specific API errors with user-friendly messages
                if "api_key" in error_str or "authentication" in error_str or "invalid" in error_str:
                    return f"➜ {ERROR_MESSAGES['api_key_invalid']}"
                elif "quota" in error_str or "limit" in error_str:
                    return f"➜ {ERROR_MESSAGES['quota_exceeded']}"
                elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                    if attempt < MAX_API_RETRIES - 1:
                        print(f"🔄 Network issue, retrying... (attempt {attempt + 1}/{MAX_API_RETRIES})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    return "➜ Network connection failed. Please check your internet connection and try again."
                elif "rate" in error_str:
                    if attempt < MAX_API_RETRIES - 1:
                        print(f"⏳ Rate limited, waiting... (attempt {attempt + 1}/{MAX_API_RETRIES})")
                        time.sleep(retry_delay * 2)
                        retry_delay *= 2
                        continue
                    return f"➜ {ERROR_MESSAGES['rate_limited']}"
                else:
                    if attempt < MAX_API_RETRIES - 1:
                        print(f"⚠️ Request failed, retrying... (attempt {attempt + 1}/{MAX_API_RETRIES})")
                        time.sleep(retry_delay)
                        continue
                    return f"➜ AI service error: {str(e)}"
        
        return "➜ Failed to generate command after multiple attempts. Please try again later."
    
    def _build_contextual_prompt(self, username: str, query: str, context) -> str:
        """
        Build AI prompt with conversation context for follow-up queries.
        
        Creates a contextually-aware prompt that includes previous conversation
        history to help the AI understand follow-up and refinement requests.
        
        Args:
            username: Current system username for personalization
            query: User's current query
            context: ConversationContext object with query history
            
        Returns:
            Formatted contextual prompt string for the AI model
        """
        base_prompt = self._build_prompt(username, query)
        
        # Get context information
        context_info = context.get_context_for_ai()
        
        if not context_info:
            # No context available, use regular prompt
            return base_prompt
        
        # Insert context into the prompt
        contextual_prompt = f"""You are a CLI/terminal command expert. This is a follow-up query in an ongoing conversation.

{context_info}
{username}: {query}

System: {self.os_name}

Rules:
1. This is a FOLLOW-UP query - consider the previous conversation context
2. The user may be asking to modify, refine, or build upon previous commands
3. Look for relationships like "make it better", "add to that", "but also", "instead", etc.
4. ONLY respond to queries that can be solved with terminal/CLI commands
5. If the query is NOT about terminal commands, respond with: "Out of context - this is not a terminal command request"
6. Give the command on first line starting with →
7. If explanation needed, add ONE line comment (max 15 words)
8. For potentially dangerous commands, add:➜ [brief risk description]
9. Multiple steps: use && or ; on same line
10. Be extremely concise - terminal users want speed

IMPORTANT: Consider these as potentially dangerous and add warnings:
- File/directory deletion (rm, rmdir with wildcards or recursive flags)
- System modifications (sudo commands, chmod 777, ownership changes)
- Disk operations (dd, mkfs, fdisk, partitioning)
- Network code execution (curl|sh, wget|bash)
- Process termination (killall, kill -9)
- System control (shutdown, reboot, halt)
- Database operations (DROP, TRUNCATE)
- Overwriting files (>, redirects to important files)

Format:
→ command
(optional: super brief note or warning)

NEVER add extra line breaks. Keep output compact."""
        
        return contextual_prompt
    
    def _build_prompt(self, username: str, query: str) -> str:
        """
        Build the AI prompt for command generation.
        
        Constructs a detailed prompt that instructs the AI on how to generate
        appropriate terminal commands with safety considerations and formatting.
        
        Args:
            username: Current system username for personalization
            query: User's natural language query
            
        Returns:
            Formatted prompt string for the AI model
        """
        return f"""You are a CLI/terminal command expert. Provide ONLY the exact command needed.

System: {self.os_name}
{username}: {query}

Rules:
1. ONLY respond to queries that can be solved with terminal/CLI commands
2. If the query is NOT about terminal commands or system tasks, respond with: "Out of context - this is not a terminal command request"
3. Give the command on first line starting with →
4. If explanation needed, add ONE line comment (max 10 words)
5. For potentially dangerous commands, add:  [brief risk description]
6. Multiple steps: use && or ; on same line
7. Be extremely concise - terminal users want speed

IMPORTANT: Consider these as potentially dangerous and add warnings:
- File/directory deletion (rm, rmdir with wildcards or recursive flags)
- System modifications (sudo commands, chmod 777, ownership changes)
- Disk operations (dd, mkfs, fdisk, partitioning)
- Network code execution (curl|sh, wget|bash)
- Process termination (killall, kill -9)
- System control (shutdown, reboot, halt)
- Database operations (DROP, TRUNCATE)
- Overwriting files (>, redirects to important files)

OUT OF CONTEXT examples (respond with "Out of context"):
- General programming questions not related to CLI
- Theoretical questions about concepts
- Personal advice or non-technical questions
- Questions about specific code logic or algorithms
- Questions about web development, UI design, etc.
- Math problems, recipes, travel advice, etc.

Format:
→ command
(optional: super brief note or warning)

Examples:
{username}: list all files
→ ls -la

{username}: find large files over 100MB
→ find . -type f -size +100M

{username}: check disk space
→ df -h

{username}: delete all .tmp files
→ find . -name "*.tmp" -delete
 deletes all .tmp files recursively

{username}: remove everything in current folder
→ rm -rf *
 permanently deletes all files and folders

{username}: how to bake a cake
Out of context - this is not a terminal command request

{username}: explain how React works
Out of context - this is not a terminal command request

NEVER add extra line breaks. Keep output compact."""
