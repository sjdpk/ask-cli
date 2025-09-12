#!/usr/bin/env python3
"""AI client for command generation"""

import getpass
import time
from config import AI_MODEL, get_os_name

# Import google.generativeai with error handling
try:
    import google.generativeai as genai
except ImportError as e:
    raise ImportError("Google Generative AI package not found. Please reinstall Ask CLI.") from e


class CommandGenerator:
    """AI-powered command generator with comprehensive error handling"""
    
    def __init__(self, api_key):
        """Initialize the command generator with API key validation"""
        if not api_key or not api_key.strip():
            raise ValueError("API key is required and cannot be empty")
            
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(AI_MODEL)
            self.os_name = get_os_name()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AI model: {str(e)}") from e
    
    def get_command(self, query):
        """Generate terminal command from natural language query with comprehensive error handling"""
        if not query or not query.strip():
            return "➜ Please provide a valid query"
            
        try:
            username = getpass.getuser()
            prompt = self._build_prompt(username, query)
            
            # Attempt to generate content with retries
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.GenerationConfig(
                            temperature=0.1,      # More deterministic
                            max_output_tokens=150 # Keep responses short
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
                        return "➜ Invalid API key. Run 'ask --reset' to update your API key."
                    elif "quota" in error_str or "limit" in error_str:
                        return "➜ API quota exceeded. Please check your Google AI Studio quota or try again later."
                    elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                        if attempt < max_retries - 1:
                            print(f"🔄 Network issue, retrying... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        return "➜ Network connection failed. Please check your internet connection and try again."
                    elif "rate" in error_str:
                        if attempt < max_retries - 1:
                            print(f"⏳ Rate limited, waiting... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay * 2)
                            retry_delay *= 2
                            continue
                        return "➜ Too many requests. Please wait a moment and try again."
                    else:
                        if attempt < max_retries - 1:
                            print(f"⚠️ Request failed, retrying... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            continue
                        return f"➜ AI service error: {str(e)}"
            
            return "➜ Failed to generate command after multiple attempts. Please try again later."
            
        except KeyboardInterrupt:
            return "➜ Operation cancelled by user"
        except Exception as e:
            error_str = str(e).lower()
            if "permission" in error_str:
                return "➜ Permission denied. Please check your system permissions."
            else:
                return f"➜ Unexpected error: {str(e)}"
    
    def _build_prompt(self, username, query):
        """Build the AI prompt for command generation"""
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
