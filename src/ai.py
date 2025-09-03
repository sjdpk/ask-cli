#!/usr/bin/env python3
"""AI client for command generation"""

import getpass
import google.generativeai as genai
from config import AI_MODEL, get_os_name


class CommandGenerator:
    """AI-powered command generator"""
    
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(AI_MODEL)
        self.os_name = get_os_name()
    
    def get_command(self, query):
        """Generate terminal command from natural language query"""
        username = getpass.getuser()
        prompt = self._build_prompt(username, query)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,      # More deterministic
                    max_output_tokens=150 # Keep responses short
                )
            )
            return response.text.strip()
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _build_prompt(self, username, query):
        """Build the AI prompt for command generation"""
        return f"""You are a CLI/terminal command expert. Provide ONLY the exact command needed.

System: {self.os_name}
{username}: {query}

Rules:
1. Give the command on first line starting with →
2. If explanation needed, add ONE line comment (max 10 words)
3. For dangerous commands (rm -rf, etc) add: ⚠️  warning
4. Multiple steps: use && or ; on same line
5. Be extremely concise - terminal users want speed

Format:
→ command
(optional: super brief note)

Examples:
{username}: list all files
→ ls -la

{username}: find large files over 100MB
→ find . -type f -size +100M

{username}: check disk space
→ df -h

{username}: delete all .tmp files
→ find . -name "*.tmp" -delete
⚠️  will delete all .tmp files recursively

NEVER add extra line breaks. Keep output compact."""
