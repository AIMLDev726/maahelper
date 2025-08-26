#!/usr/bin/env python3
"""
MaaHelper - Command Line Entry Point
Handles --help and --version before any CLI initialization
"""

import sys
import asyncio
from rich.console import Console

console = Console()

def show_help():
    """Show help information and exit"""
    from rich.panel import Panel
    from rich.align import Align

    # Import version safely
    try:
        from maahelper import __version__
    except ImportError:
        __version__ = "0.0.5"

    help_content = f"""[bold blue]🤖 MaaHelper v{__version__}[/bold blue]
[dim]Advanced AI-Powered Coding Assistant[/dim]
👨‍💻 Created by Meet Solanki (AIML Student)

[bold green]🚀 USAGE:[/bold green]
  [cyan]maahelper[/cyan] [OPTIONS]
  [cyan]python -m maahelper[/cyan] [OPTIONS]

[bold green]📝 OPTIONS:[/bold green]
  [cyan]-h, --help[/cyan]              Show this help message and exit
  [cyan]-v, --version[/cyan]           Show version information and exit
  [cyan]-s, --session SESSION[/cyan]   Session ID for conversation history
  [cyan]-w, --workspace WORKSPACE[/cyan] Workspace directory path

[bold green]✨ FEATURES:[/bold green]
  • [yellow]Multi-Provider Support[/yellow] - OpenAI, Groq, Anthropic, Google, Ollama
  • [yellow]Real-time Streaming[/yellow] - Live AI responses with Rich formatting
  • [yellow]File Analysis[/yellow] - AI-powered code analysis with file-search command
  • [yellow]Rich UI[/yellow] - Beautiful terminal interface with colors and panels
  • [yellow]Persistent Sessions[/yellow] - Conversation history across sessions
  • [yellow]Real-time Analysis[/yellow] - Live code feedback and error detection
  • [yellow]Git Integration[/yellow] - AI-powered commit messages and branch names

[bold green]🎯 EXAMPLES:[/bold green]
  [dim]# Start with default settings[/dim]
  [cyan]maahelper[/cyan]
  
  [dim]# Custom session and workspace[/dim]
  [cyan]maahelper --session my_project --workspace /path/to/project[/cyan]

[bold green]💡 COMMANDS (once running):[/bold green]
  [cyan]help[/cyan]                    Show comprehensive help
  [cyan]prompts[/cyan]                 🆕 List custom AI agent prompts
  [cyan]code-review[/cyan]             🆕 AI-powered code review
  [cyan]bug-analysis[/cyan]            🆕 Deep bug analysis & solutions
  [cyan]explain-concept[/cyan]         🆕 Programming concept explanations
  [cyan]optimize-performance[/cyan]    🆕 Performance optimization analysis
  [cyan]file-search <path>[/cyan]      Analyze any file with AI
  [cyan]analyze-workspace[/cyan]       Analyze entire workspace for issues
  [cyan]discover-models[/cyan]         Auto-discover latest AI models
  [cyan]git-commit[/cyan]              AI-powered smart commit messages
  [cyan]files[/cyan]                   Show workspace files
  [cyan]status[/cyan]                  Show current configuration
  [cyan]clear[/cyan]                   Clear conversation history
  [cyan]exit[/cyan]                    Exit the application

[bold yellow]🔧 Setup:[/bold yellow] Set environment variables for API keys:
  • GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
  • Or use the interactive setup on first run

[bold green]🆕 NEW in v{__version__}:[/bold green]
  • Dynamic model discovery with real-time availability
  • Real-time code analysis with file watching
  • Enhanced Git integration with AI-powered workflows
  • Improved error handling and tool call compatibility"""

    panel = Panel.fit(
        Align.center(help_content),
        title="[bold green]MaaHelper - AI Coding Assistant[/bold green]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)

def show_version():
    """Show version information and exit"""
    from rich.panel import Panel
    from rich.align import Align

    # Import version safely
    try:
        from maahelper import __version__
    except ImportError:
        __version__ = "0.0.5"

    version_content = f"""[bold blue]🤖 MaaHelper v{__version__}[/bold blue]

[bold green]Version Information:[/bold green]
  • Version: {__version__}
  • Author: Meet Solanki (AIML Student)
  • License: MIT
  • Repository: https://github.com/AIMLDev726/maahelper

[bold green]Features in this version:[/bold green]
  • Enhanced tool call error handling
  • Dynamic model discovery
  • Real-time code analysis
  • Git integration improvements
  • Multi-provider AI support

[bold green]Supported Providers:[/bold green]
  • OpenAI (GPT-4, GPT-3.5)
  • Groq (Llama, Mixtral, Gemma)
  • Anthropic (Claude 3.5, Claude 3)
  • Google (Gemini Pro)
  • Ollama (Local models)"""

    panel = Panel.fit(
        Align.center(version_content),
        title="[bold blue]Version Information[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)

def main():
    """Main entry point that handles arguments before CLI initialization"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Handle help and version immediately - no CLI initialization needed
    for arg in args:
        if arg in ['-h', '--help']:
            show_help()
            sys.exit(0)
        elif arg in ['-v', '--version']:
            show_version()
            sys.exit(0)
    
    # If we get here, either no arguments or other arguments
    # Delegate to the main CLI system
    try:
        from maahelper.__main__ import main as main_entry
        main_entry()
    except Exception as e:
        console.print(f"[red]❌ Error starting MaaHelper: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
