#!/usr/bin/env python3
"""Main entry point for ask CLI"""

import sys
from commands import handle_help, handle_reset, handle_update, handle_query


def main():
    """Main entry point"""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: ask <what you want to do>")
        print("Try:   ask list all files")
        print("       ask --help")
        sys.exit(1)

    # Check for --execute or -e flag and --force or -f flag
    execute = False
    force = False
    
    if '--execute' in sys.argv:
        sys.argv.remove('--execute')
        execute = True
    elif '-e' in sys.argv:
        sys.argv.remove('-e')
        execute = True
    
    if '--force' in sys.argv:
        sys.argv.remove('--force')
        force = True
    elif '-f' in sys.argv:
        sys.argv.remove('-f')
        force = True

    # Handle special commands (only exact matches)
    if sys.argv[1] in ['-h', '--help'] or (sys.argv[1] == 'help' and len(sys.argv) == 2):
        handle_help()
    elif sys.argv[1] == '--reset':
        handle_reset()
    elif sys.argv[1] == '--update':
        handle_update()

    # Handle regular query
    query = ' '.join(sys.argv[1:])
    handle_query(query, execute, force)


if __name__ == "__main__":
    main()
