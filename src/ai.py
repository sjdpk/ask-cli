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
        # Platform-specific example commands
        if self.os_name == "Windows":
            list_cmd = "dir"
            find_cmd = "where /r . *.tmp"
            space_cmd = "dir"
            process_cmd = "netstat -ano | findstr :3000"
            compress_cmd = "powershell Compress-Archive -Path . -DestinationPath archive.zip"
        else:
            list_cmd = "ls -la"
            find_cmd = "find . -name \"*.tmp\" -delete"
            space_cmd = "df -h"
            process_cmd = "lsof -ti:3000 | xargs kill -9"
            compress_cmd = "tar -czf archive.tar.gz ."
        
        return f"""You are a CLI/terminal command expert. Provide ONLY the exact command needed for {self.os_name}.

System: {self.os_name}
{username}: {query}

Rules:
1. ONLY respond to queries that can be solved with terminal/CLI commands
2. If the query is NOT about terminal commands or system tasks, respond with: "Out of context - this is not a terminal command request"
3. Give the command on first line starting with →
4. If explanation needed, add ONE line comment (max 10 words)
5. For potentially dangerous commands, add: ⚠️ [brief risk description]
6. Multiple steps: use && or ; on same line (use & for Windows)
7. Be extremely concise - terminal users want speed
8. Use {self.os_name}-specific commands and syntax

IMPORTANT: Consider these as potentially dangerous and add ⚠️ warnings:
- File/directory deletion (rm, rmdir, del with wildcards or recursive flags)
- System modifications (sudo commands, chmod 777, ownership changes, admin rights)
- Disk operations (dd, mkfs, fdisk, format, diskpart)
- Network code execution (curl|sh, wget|bash, downloading and running scripts)
- Process termination (killall, kill -9, taskkill /f)
- System control (shutdown, reboot, halt, restart-computer)
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
(optional: super brief note or ⚠️ warning)

Examples for {self.os_name}:
{username}: list all files
→ {list_cmd}

{username}: find large files over 100MB
→ {"forfiles /s /m *.* /c \"cmd /c if @fsize gtr 104857600 echo @path\"" if self.os_name == "Windows" else "find . -type f -size +100M"}

{username}: check disk space
→ {space_cmd}

{username}: delete all .tmp files
→ {find_cmd}
⚠️ deletes all .tmp files recursively

{username}: remove everything in current folder
→ {"del /s /q * && for /d %d in (*) do rmdir /s /q \"%d\"" if self.os_name == "Windows" else "rm -rf *"}
⚠️ permanently deletes all files and folders

{username}: how to bake a cake
Out of context - this is not a terminal command request

{username}: explain how React works
Out of context - this is not a terminal command request

NEVER add extra line breaks. Keep output compact."""
