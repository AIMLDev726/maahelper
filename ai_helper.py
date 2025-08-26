#!/usr/bin/env python3
"""
MaaHelper - Rich CLI Entry Point
Direct entry to avoid module warnings
"""

import asyncio
import sys

async def main():
    """Direct entry point"""
    # Import the CLI components
    from maahelper.cli.modern_enhanced_cli import main as cli_main
    # Run the CLI
    await cli_main()

if __name__ == "__main__":
    asyncio.run(main())
