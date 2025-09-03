#!/usr/bin/env python3
"""User interface utilities"""

import time
import threading


def show_spinner(stop_event):
    """Display animated spinner while processing"""
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    
    while not stop_event.is_set():
        print(f"\r{spinner_chars[i % len(spinner_chars)]} Thinking...", 
              end="", flush=True)
        time.sleep(0.08)
        i += 1
    
    # Clear the spinner line
    print("\r" + " " * 20 + "\r", end="", flush=True)


class SpinnerContext:
    """Context manager for spinner display"""
    
    def __enter__(self):
        self.stop_event = threading.Event()
        self.spinner_thread = threading.Thread(target=show_spinner, args=(self.stop_event,))
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_event.set()
        self.spinner_thread.join(timeout=0.3)
