#!/usr/bin/env python3
"""
User interface utilities with comprehensive error handling

This module provides UI components and utilities for the ask CLI,
including spinners and other interactive elements.
"""

import time
import threading
import sys
from typing import Optional

# Import constants
from constants import SPINNER_CHARS, SPINNER_DELAY, SPINNER_CLEAR_WIDTH


def show_spinner(stop_event: threading.Event) -> None:
    """
    Display animated spinner while processing operations.
    
    Shows a rotating spinner animation to indicate that the application
    is working on a task, with graceful error handling for display issues.
    
    Args:
        stop_event: Threading event to signal when to stop the spinner
        
    Side Effects:
        Prints spinner animation to stdout until stop_event is set
    """
    i = 0
    
    try:
        while not stop_event.is_set():
            try:
                print(f"\r{SPINNER_CHARS[i % len(SPINNER_CHARS)]} Thinking...", 
                      end="", flush=True)
                time.sleep(SPINNER_DELAY)
                i += 1
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully in spinner thread
                break
            except Exception:
                # Silently handle any printing errors and continue
                time.sleep(SPINNER_DELAY)
                i += 1
    except Exception:
        # Silently handle any unexpected errors in spinner thread
        pass
    finally:
        # Always try to clear the spinner line
        try:
            print("\r" + " " * SPINNER_CLEAR_WIDTH + "\r", end="", flush=True)
        except Exception:
            # If we can't clear, at least try to move to next line
            try:
                print()
            except Exception:
                pass


class SpinnerContext:
    """
    Context manager for spinner display with comprehensive error handling.
    
    Provides a convenient way to display a spinner during long-running operations
    using Python's context manager protocol for automatic cleanup.
    """
    
    def __init__(self):
        """Initialize the spinner context manager."""
        self.stop_event: Optional[threading.Event] = None
        self.spinner_thread: Optional[threading.Thread] = None
    
    def __enter__(self) -> 'SpinnerContext':
        """
        Start the spinner when entering the context.
        
        Returns:
            Self for method chaining
        """
        try:
            self.stop_event = threading.Event()
            self.spinner_thread = threading.Thread(target=show_spinner, args=(self.stop_event,))
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
            return self
        except Exception:
            # If spinner fails to start, continue without it
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        """
        Stop the spinner when exiting the context.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
            
        Returns:
            None to allow exceptions to propagate, False for KeyboardInterrupt
        """
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
                print("\r" + " " * SPINNER_CLEAR_WIDTH + "\r", end="", flush=True)
            except Exception:
                pass
            return False  # Don't suppress KeyboardInterrupt
        
        return None
