#!/usr/bin/env python3
"""Main entry point for ask CLI"""

import sys
from commands import handle_help, handle_reset, handle_query


def main():
    """Main entry point"""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: ask <what you want to do>")
        print("Try:   ask list all files")
        print("       ask --help")
        sys.exit(1)
    
    # Handle special commands
    if sys.argv[1] in ['-h', '--help', 'help']:
        handle_help()
    elif sys.argv[1] == '--reset':
        handle_reset()
    
    # Handle regular query
    query = ' '.join(sys.argv[1:])
    handle_query(query)


if __name__ == "__main__":
    main()
