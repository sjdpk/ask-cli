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
            return f"Error: {str(e)}"
    
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
