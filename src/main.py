#!/usr/bin/env python3
"""Main entry point for ask CLI"""

import sys

def main():
    """Main entry point with comprehensive exception handling"""
    try:
        # Import commands here to handle import errors gracefully
        from commands import handle_help, handle_reset, handle_update, handle_query
        
        # Parse command line arguments
        if len(sys.argv) < 2:
            print("Usage: ask <what you want to do>")
            print("Try:   ask list all files")
            print("       ask --help")
            sys.exit(1)

        # Check for --execute or -e flag and --force or -f flag
        execute = False
        force = False
        
        try:
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
        except ValueError as e:
            # Handle edge cases with argument parsing
            print("➜ Error parsing command line arguments.")
            print("Usage: ask <what you want to do>")
            sys.exit(1)

        try:
            # Handle special commands (only exact matches)
            if sys.argv[1] in ['-h', '--help'] or (sys.argv[1] == 'help' and len(sys.argv) == 2):
                handle_help()
            elif sys.argv[1] == '--reset':
                handle_reset()
            elif sys.argv[1] == '--update':
                handle_update()

            # Handle regular query
            query = ' '.join(sys.argv[1:])
            if not query.strip():
                print("➜ Please provide a query.")
                print("Usage: ask <what you want to do>")
                sys.exit(1)
                
            handle_query(query, execute, force)
            
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            sys.exit(0)
        except SystemExit:
            # Allow normal sys.exit() calls to pass through
            raise
        except Exception as e:
            print(f"➜ Error processing command: {str(e)}")
            print("   Try: ask --help for usage information")
            sys.exit(1)
            
    except ImportError as e:
        print("➜ Failed to load required components.")
        print("   Please ensure Ask CLI is properly installed.")
        print("   Reinstall using: curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"➜ Unexpected error in main: {str(e)}")
        print("   Please report this issue on GitHub if it persists.")
        sys.exit(1)


if __name__ == "__main__":
    main()
