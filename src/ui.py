#!/usr/bin/env python3
"""User interface utilities with comprehensive error handling"""

import time
import threading
import sys


def show_spinner(stop_event):
    """Display animated spinner while processing with error handling"""
    spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    
    try:
        while not stop_event.is_set():
            try:
                print(f"\r{spinner_chars[i % len(spinner_chars)]} Thinking...", 
                      end="", flush=True)
                time.sleep(0.08)
                i += 1
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully in spinner thread
                break
            except Exception:
                # Silently handle any printing errors and continue
                time.sleep(0.08)
                i += 1
    except Exception:
        # Silently handle any unexpected errors in spinner thread
        pass
    finally:
        # Always try to clear the spinner line
        try:
            print("\r" + " " * 20 + "\r", end="", flush=True)
        except Exception:
            # If we can't clear, at least try to move to next line
            try:
                print()
            except Exception:
                pass


class SpinnerContext:
    """Context manager for spinner display with comprehensive error handling"""
    
    def __init__(self):
        self.stop_event = None
        self.spinner_thread = None
    
    def __enter__(self):
        try:
            self.stop_event = threading.Event()
            self.spinner_thread = threading.Thread(target=show_spinner, args=(self.stop_event,))
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
            return self
        except Exception:
            # If spinner fails to start, continue without it
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.stop_event:
                self.stop_event.set()
            if self.spinner_thread:
                self.spinner_thread.join(timeout=0.5)
        except Exception:
            # Silently handle cleanup errors
            pass
        
        # Handle KeyboardInterrupt specially
        if exc_type is KeyboardInterrupt:
            try:
                print("\r" + " " * 20 + "\r", end="", flush=True)
            except Exception:
                pass
            return False  # Don't suppress KeyboardInterrupt
