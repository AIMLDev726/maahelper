#!/usr/bin/env python3
"""
MaaHelper - Main Entry Point
Allows running the package with: python -m maahelper
"""

import sys
import asyncio
from pathlib import Path

def main():
    """Main entry point for python -m maahelper"""
    try:
        # Check for command-line arguments first
        args = sys.argv[1:] if len(sys.argv) > 1 else []

        # Handle help and version directly
        if any(arg in ['-h', '--help'] for arg in args):
            from .cli.modern_enhanced_cli import show_rich_help
            show_rich_help()
            return

        if any(arg in ['-v', '--version'] for arg in args):
            from .cli.modern_enhanced_cli import show_rich_version
            show_rich_version()
            return

        # If arguments are provided, use the enhanced CLI directly
        if args:
            from .cli.modern_enhanced_cli import main as cli_main
            cli_main()
        else:
            # No arguments, use the CLI selector for interactive setup
            from .cli.modern_cli_selector import cli_selector_entry
            cli_selector_entry()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting MaaHelper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
