"""
MaaHelper - Modern Enhanced CLI
Streamlined implementation using OpenAI client and Rich UI
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.align import Align
from rich.columns import Columns

# Internal imports
from ..core.llm_client import UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models
from ..utils.streaming import ModernStreamingHandler, ConversationManager
from ..managers.streamlined_api_key_manager import api_key_manager
from ..utils.streamlined_file_handler import file_handler

console = Console()

class ModernEnhancedCLI:
    """Modern Enhanced CLI with OpenAI client integration"""
    
    def __init__(self, session_id: str = "default", workspace_path: str = "."):
        self.session_id = f"modern_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.workspace_path = Path(workspace_path).resolve()
        
        # Initialize components
        self.llm_client: Optional[UnifiedLLMClient] = None
        self.conversation_manager: Optional[ConversationManager] = None
        self.current_provider = ""
        self.current_model = ""
        
        # Setup file handler
        file_handler.workspace_path = self.workspace_path
        
        # System prompt
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt"""
        return f"""You are MaaHelper v0.0.4 — a professional AI programming assistant developed by Meet Solanki (AIML Student). Your goal is to deliver accurate, context-aware coding help with intelligent file-level understanding.

== SYSTEM OVERVIEW ==
• Name        : MaaHelper v0.0.4
• Creator     : Meet Solanki (AIML Student)
• Objective   : Advanced programming assistance with workspace-level file processing
• Guiding Goal: Boost developer productivity through AI-powered problem-solving

== CORE CAPABILITIES ==
• Code debugging, refactoring, and optimization
• Support for Python, JavaScript, TypeScript, and other major languages
• Handles complex file processing: code, docs, configs, data files
• Real-time, token-efficient response generation (streaming enabled)
• Generates contextual recommendations based on code structure and logic

== FILE CONTEXT ==
• Workspace Access : {self.workspace_path}
• Use `file-search <filepath>` for deep file analysis and QA
• Provide summaries, explanations, fixes, or refactors of code segments
• Retain workspace context to improve interactive help

== INTERACTION BEHAVIOR ==
• Respond with clear, actionable steps
• Provide code examples and reasoning
• Ask for clarification when needed
• Avoid unnecessary verbosity
• Prioritize accuracy, helpfulness, and technical clarity

== ETHOS ==
MaaHelper is designed to support developers not just with solutions but also learning. Stay focused, concise, and deeply helpful. Always act like a senior developer guiding a peer.

Session ID : {self.session_id}
Your intelligent coding assistant is ready. Awaiting command.
"""


    async def setup_llm_client(self) -> bool:
        """Setup LLM client with provider selection"""
        try:
            # Welcome animation
            with console.status("[bold blue]Initializing MaaHelper...", spinner="dots"):
                await asyncio.sleep(1)  # Brief pause for effect
            
            console.print()
            console.print(Panel.fit(
                Align.center(
                    "[bold blue]🤖 MaaHelper v0.0.4[/bold blue]\n"
                    "[dim]Modern Enhanced CLI with Multi-Provider Support[/dim]\n\n"
                    "👨‍💻 Created by Meet Solanki (AIML Student)\n"
                    "[green]✨ Rich UI • 🚀 Live Streaming • 🔍 File Analysis[/green]"
                ),
                title="🌟 Welcome to the Future of AI Assistance",
                border_style="blue",
                padding=(1, 2)
            ))
            
            # Check available providers with spinner
            with console.status("[bold green]Checking API keys...", spinner="earth"):
                await asyncio.sleep(0.5)  # Brief pause for effect
                available_providers = api_key_manager.get_available_providers()
            
            if not available_providers:
                console.print()
                error_panel = Panel.fit(
                    Align.center(
                        "[bold red]❌ No API Keys Found[/bold red]\n\n"
                        "[yellow]To get started, set up your API keys:[/yellow]\n"
                        "• Set environment variables (GROQ_API_KEY, OPENAI_API_KEY, etc.)\n"
                        "• Or use the API key manager\n\n"
                        "[dim]💡 Tip: Get free API keys from Groq for instant access![/dim]"
                    ),
                    title="⚠️ Setup Required",
                    border_style="red",
                    padding=(1, 2)
                )
                console.print(error_panel)
                return False
                
            # Show available providers with beautiful formatting
            provider_columns = Columns([
                f"[bold green]✅ {provider.upper()}[/bold green]" 
                for provider in available_providers
            ], equal=True, expand=True)
            
            console.print(Panel.fit(
                Align.center(provider_columns),
                title="🔑 Available AI Providers",
                border_style="green",
                padding=(1, 2)
            ))
            
            # Provider selection with Rich formatting
            if len(available_providers) == 1:
                selected_provider = available_providers[0]
                console.print(Panel.fit(
                    f"[bold cyan]🎯 Auto-selected: {selected_provider.upper()}[/bold cyan]",
                    border_style="cyan"
                ))
            else:
                console.print()
                provider_table = Table(title="🤖 Select Your AI Provider", show_header=False, box=None)
                provider_table.add_column("", style="cyan", width=4)
                provider_table.add_column("", style="bold", width=20)
                provider_table.add_column("", style="dim", width=30)
                
                provider_descriptions = {
    "openai": "Official GPT-3.5 / GPT-4 API from OpenAI",
    "groq": "Ultra-fast inference with LLaMA / Mixtral models",
    "anthropic": "Claude models, excellent reasoning",
    "google": "Gemini models, multimodal support",
    "ollama": "Run local models with OpenAI-compatible API",
    "together": "Free access to Mistral, LLaMA, Mixtral etc",
    "fireworks": "Supports Mistral and StableCode inference",
    "openrouter": "Unified gateway to multiple model providers",
    "localai": "Self-hosted OpenAI-compatible API",
    "deepinfra": "Cloud-based fast inference for open models",
    "perplexity": "R1 and mix models via OpenRouter compatible",
    "cerebras": "Inference on Cerebras Wafer-Scale Engine"
}

                
                for i, provider in enumerate(available_providers, 1):
                    desc = provider_descriptions.get(provider, "Advanced AI capabilities")
                    provider_table.add_row(f"{i}.", provider.upper(), desc)
                
                console.print(provider_table)
                console.print()
                    
                while True:
                    try:
                        choice = Prompt.ask("[bold cyan]🎯 Choose provider[/bold cyan]", default="1")
                        idx = int(choice) - 1
                        if 0 <= idx < len(available_providers):
                            selected_provider = available_providers[idx]
                            break
                        else:
                            console.print("[red]❌ Invalid choice. Please try again.[/red]")
                    except ValueError:
                        console.print("[red]❌ Please enter a number.[/red]")
            
            # Model selection with Rich formatting  
            with console.status(f"[bold green]Loading models for {selected_provider.upper()}...", spinner="dots"):
                await asyncio.sleep(0.5)  # Brief pause for effect
                available_models = get_provider_models(selected_provider)
            
            console.print()

            # Always prompt the user for model name regardless of available_models
            if available_models:
                console.print()
                console.print(f"[bold green]📦 Available models:[/bold green] {', '.join(available_models[:5])}")
                model_input = Prompt.ask(f"🧠 Enter the model name for {selected_provider.upper()}")
            else:
                console.print()
                console.print(f"[yellow]⚠ No models detected. Please enter model name manually for {selected_provider.upper()}[/yellow]")
                model_input = Prompt.ask(f"🧠 Enter the model name for {selected_provider.upper()}")

            selected_model = model_input.strip()

            console.print(Panel.fit(
                    f"[bold cyan]🎯 Selected model: {selected_model}[/bold cyan]",
                    border_style="cyan"
                ))

                        
            # if len(available_models) <= 1:
            #     selected_model = available_models[0] if available_models else "default"
            #     console.print(Panel.fit(
            #         f"[bold cyan]🎯 Using model: {selected_model}[/bold cyan]",
            #         border_style="cyan"
            #     ))
            # else:
            #     console.print()
            #     model_table = Table(title=f"🧠 Select Model for {selected_provider.upper()}", show_header=False, box=None)
            #     model_table.add_column("", style="cyan", width=4)
            #     model_table.add_column("", style="bold", width=30)
                
            #     for i, model in enumerate(available_models[:5], 1):  # Show top 5 models
            #         model_table.add_row(f"{i}.", model)
                
            #     console.print(model_table)
            #     console.print()
                    
            # while True:
            #         try:
            #             choice = Prompt.ask("[bold cyan]🧠 Choose model[/bold cyan]", default="1")
            #             idx = int(choice) - 1
            #             if 0 <= idx < len(available_models):
            #                 selected_model = available_models[idx]
            #                 break
            #             else:
            #                 console.print("[red]❌ Invalid choice. Please try again.[/red]")
            #         except ValueError:
            #             console.print("[red]❌ Please enter a number.[/red]")
            
            # Setup with progress animation
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task1 = progress.add_task("[green]Getting API key...", total=100)
                await asyncio.sleep(0.3)
                progress.update(task1, advance=50)
                
                api_key = api_key_manager.get_api_key(selected_provider)
                if not api_key:
                    console.print(Panel.fit(
                        f"[bold red]❌ Could not get API key for {selected_provider}[/bold red]",
                        border_style="red"
                    ))
                    return False
                progress.update(task1, advance=50)
                
                task2 = progress.add_task("[green]Creating LLM client...", total=100)
                await asyncio.sleep(0.3)
                self.llm_client = create_llm_client(selected_provider, selected_model, api_key)
                progress.update(task2, advance=50)
                
                task3 = progress.add_task("[green]Initializing conversation...", total=100)
                await asyncio.sleep(0.3)
                self.conversation_manager = ConversationManager(self.llm_client, self.session_id)
                progress.update(task3, advance=50)
                
                self.current_provider = selected_provider
                self.current_model = selected_model
                progress.update(task2, advance=50)
                progress.update(task3, advance=50)
            
            # Success panel with all details
            console.print()
            success_content = f"""[bold green]✅ Setup Complete![/bold green]

[cyan]🤖 Provider:[/cyan] [bold]{selected_provider.upper()}[/bold]
[cyan]🧠 Model:[/cyan] [bold]{selected_model}[/bold]
[cyan]📁 Workspace:[/cyan] [dim]{self.workspace_path}[/dim]
[cyan]🔗 Session:[/cyan] [dim]{self.session_id}[/dim]

[green]🚀 Ready for AI-powered assistance![/green]
[yellow]💡 Type 'help' for commands or start chatting![/yellow]"""
            
            console.print(Panel.fit(
                Align.center(success_content),
                title="🎉 MaaHelper Ready",
                border_style="green",
                padding=(1, 2)
            ))
            
            return True
            
        except Exception as e:
            console.print(Panel.fit(
                f"[bold red]❌ Setup failed: {e}[/bold red]",
                border_style="red"
            ))
            return False
    
    async def show_help(self):
        """Show comprehensive help"""
        help_content = f"""
# 🤖 MaaHelper v0.0.4 - Modern Enhanced CLI

## 📝 Basic Commands
- `help` - Show this help message
- `exit`, `quit`, `bye` - Exit the application  
- `clear` - Clear conversation history
- `status` - Show current configuration
- `files` - Show directory structure and supported files

## 📁 File Operations
- `file-search <filepath>` - AI-powered file analysis and summary
- `dir` - Show directory structure only
- `files table` - Show supported files in a table

## 🔧 Configuration
- `switch provider` - Change AI provider
- `switch model` - Change model
- `providers` - List available providers
- `models` - List models for current provider

## 💡 Features
- **Real-time streaming** responses for immediate feedback
- **Multi-provider support** (OpenAI, Groq, Anthropic, Google, Ollama)
- **Intelligent file processing** with AI analysis
- **Rich formatting** with syntax highlighting
- **Persistent conversation** history per session

## 🎯 Current Configuration
- **Provider:** {self.current_provider.upper()}
- **Model:** {self.current_model}  
- **Workspace:** {self.workspace_path}
- **Session:** {self.session_id}

## 📚 Examples
- `file-search src/main.py` - Analyze Python file
- `What's the difference between async and sync?` - Ask programming questions
- `Review this code for bugs` - After using file-search
- `How can I optimize this algorithm?` - Get optimization suggestions

💡 **Pro Tips:**
- Files analyzed with `file-search` are added to conversation context
- Ask follow-up questions about analyzed files
- Use specific programming questions for best results
- Combine file analysis with coding assistance

🚀 **Ready to help you code better!**
"""
        console.print(Markdown(help_content))
    
    async def show_status(self):
        """Show current status"""
        # Get conversation stats
        stats = self.conversation_manager.get_stats() if self.conversation_manager else {}
        
        # Get file stats
        supported_files = file_handler.list_supported_files(100)
        file_types = {}
        for file_info in supported_files:
            ftype = file_info['type']
            file_types[ftype] = file_types.get(ftype, 0) + 1
        
        table = Table(title="📊 Session Status", show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Value", style="green", width=30)
        
        table.add_row("Provider", self.current_provider.upper())
        table.add_row("Model", self.current_model)
        table.add_row("Session ID", self.session_id)
        table.add_row("Workspace", str(self.workspace_path))
        table.add_row("Total Messages", str(stats.get('total_messages', 0)))
        table.add_row("User Messages", str(stats.get('user_messages', 0))) 
        table.add_row("AI Messages", str(stats.get('assistant_messages', 0)))
        table.add_row("Supported Files", str(len(supported_files)))
        table.add_row("File Types", ", ".join(file_types.keys())[:50] + ("..." if len(file_types) > 5 else ""))
        
        console.print()
        console.print(table)
        console.print()
    
    async def process_command(self, user_input: str) -> bool:
        """Process special commands, return True if handled"""
        command = user_input.lower().strip()
        
        if command in ['exit', 'quit', 'bye']:
            console.print("👋 [bold blue]Thank you for using MaaHelper![/bold blue]")
            console.print("[dim]Created by Meet Solanki (AIML Student)[/dim]")
            return True
            
        elif command == 'help':
            await self.show_help()
            return False
            
        elif command == 'clear':
            if self.conversation_manager:
                self.conversation_manager.clear_history()
            return False
            
        elif command == 'status':
            await self.show_status()
            return False
            
        elif command == 'files':
            file_handler.show_supported_files_table()
            return False
            
        elif command == 'files table':
            file_handler.show_supported_files_table()
            return False
            
        elif command == 'dir':
            file_handler.show_directory_structure(show_files=False)
            return False
            
        elif command.startswith('file-search '):
            filepath = command[12:].strip()
            if not filepath:
                console.print("[red]Usage: file-search <filepath>[/red]")
                return False
            
            await file_handler.file_search_command(filepath, self.llm_client)
            return False
            
        elif command == 'providers':
            providers = api_key_manager.get_available_providers()
            console.print(f"[green]Available providers:[/green] {', '.join(providers)}")
            return False
            
        elif command == 'models':
            models = get_provider_models(self.current_provider)
            console.print(f"[green]Models for {self.current_provider.upper()}:[/green]")
            for model in models[:10]:  # Show first 10
                console.print(f"  • {model}")
            return False
            
        return False  # Command not handled
    
    async def main_loop(self):
        """Main interaction loop with Rich formatting"""
        console.print()
        welcome_panel = Panel.fit(
            Align.center(
                "[bold green]🎉 MaaHelper Ready![/bold green]\n\n"
                "[yellow]💬 Start chatting or try these commands:[/yellow]\n"
                "• [cyan]help[/cyan] - Show all commands\n"
                "• [cyan]files[/cyan] - Browse workspace files\n"
                "• [cyan]file-search <path>[/cyan] - Analyze any file with AI\n"
                "• [cyan]status[/cyan] - Check current configuration\n\n"
                "[dim]✨ Everything is beautifully formatted with Rich UI![/dim]"
            ),
            title="✨ Welcome to Your AI Assistant",
            border_style="green",
            padding=(1, 2)
        )
        console.print(welcome_panel)
        console.print()
        
        # Show initial workspace info with Rich formatting
        file_handler.show_directory_structure(max_depth=2, show_files=False)
        
        while True:
            try:
                # Rich-formatted user input prompt
                console.print()
                user_input = Prompt.ask(
                    "[bold cyan]💬 You[/bold cyan]",
                    default="",
                    show_default=False
                ).strip()
                
                if not user_input:
                    console.print("[dim]💡 Tip: Type something to chat or 'help' for commands[/dim]")
                    continue
                
                # Process special commands with Rich feedback
                should_exit = await self.process_command(user_input)
                if should_exit:
                    break
                
                # Regular AI conversation with Rich status
                if self.conversation_manager:
                    console.print()
                    with console.status("[bold blue]🤖 AI is thinking...", spinner="dots"):
                        await asyncio.sleep(0.2)  # Brief pause for effect
                    await self.conversation_manager.chat(user_input, self.system_prompt)
                else:
                    console.print(Panel.fit(
                        "[bold red]❌ AI client not initialized[/bold red]\n"
                        "[yellow]Please restart the application[/yellow]",
                        border_style="red"
                    ))
                    
            except KeyboardInterrupt:
                console.print()
                goodbye_panel = Panel.fit(
                    Align.center(
                        "[bold blue]👋 Thank you for using MaaHelper![/bold blue]\n\n"
                        "[green]✨ Created by Meet Solanki (AIML Student)[/green]\n"
                        "[dim]Hope you enjoyed the Rich CLI experience![/dim]"
                    ),
                    title="👋 Goodbye",
                    border_style="blue",
                    padding=(1, 2)
                )
                console.print(goodbye_panel)
                break
            except Exception as e:
                console.print(Panel.fit(
                    f"[bold red]❌ Error: {e}[/bold red]",
                    border_style="red"
                ))
    
    async def start(self):
        """Start the modern enhanced CLI"""
        try:
            # Setup LLM client
            if not await self.setup_llm_client():
                console.print("[red]❌ Failed to setup AI client. Exiting.[/red]")
                return
            
            # Start main loop
            await self.main_loop()
            
        except KeyboardInterrupt:
            console.print("\n👋 [bold blue]Goodbye![/bold blue]")
        except Exception as e:
            console.print(f"[red]❌ Fatal error: {e}[/red]")


def create_cli(session_id: str = "default", workspace_path: str = ".") -> ModernEnhancedCLI:
    """Factory function to create CLI instance"""
    return ModernEnhancedCLI(session_id, workspace_path)


def show_rich_help():
    """Show Rich-formatted help"""
    help_panel = Panel.fit(
        """[bold blue]🤖 MaaHelper v0.0.4[/bold blue]
[dim]Modern Enhanced CLI with Multi-Provider Support[/dim]
👨‍💻 Created by Meet Solanki (AIML Student)

[bold green]🚀 USAGE:[/bold green]
  [cyan]python -m ai_helper_agent.cli.modern_enhanced_cli[/cyan] [OPTIONS]
  [cyan]ai-helper[/cyan] [OPTIONS]

[bold green]📝 OPTIONS:[/bold green]
  [cyan]-h, --help[/cyan]              Show this help message
  [cyan]-s, --session SESSION[/cyan]   Session ID for conversation history
  [cyan]-w, --workspace WORKSPACE[/cyan] Workspace directory path  
  [cyan]-v, --version[/cyan]           Show version information

[bold green]✨ FEATURES:[/bold green]
  • [yellow]Multi-Provider Support[/yellow] - OpenAI, Groq, Anthropic, Google, Ollama
  • [yellow]Real-time Streaming[/yellow] - Live AI responses with Rich formatting
  • [yellow]File Analysis[/yellow] - AI-powered code analysis with file-search command
  • [yellow]Rich UI[/yellow] - Beautiful terminal interface with colors and panels
  • [yellow]Persistent Sessions[/yellow] - Conversation history across sessions

[bold green]🎯 EXAMPLES:[/bold green]
  [dim]# Start with default settings[/dim]
  [cyan]python -m ai_helper_agent.cli.modern_enhanced_cli[/cyan]
  
  [dim]# Custom session and workspace[/dim]
  [cyan]ai-helper --session my_project --workspace /path/to/project[/cyan]

[bold green]💡 COMMANDS (once running):[/bold green]
  [cyan]help[/cyan]                    Show comprehensive help
  [cyan]file-search <path>[/cyan]      Analyze any file with AI
  [cyan]files[/cyan]                   Show workspace files
  [cyan]status[/cyan]                  Show current configuration
  [cyan]providers[/cyan]               List available AI providers
  [cyan]clear[/cyan]                   Clear conversation history
  [cyan]exit[/cyan]                    Exit the application

[bold yellow]🔧 Setup:[/bold yellow] Set environment variables for API keys:
  • GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.

[bold green]Ready to revolutionize your coding experience! 🚀[/bold green]""",
        title="🤖 MaaHelper v0.0.4 - Help",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(help_panel)

def show_rich_version():
    """Show Rich-formatted version"""
    version_panel = Panel.fit(
        """[bold blue]🤖 MaaHelper[/bold blue]
[green]Version:[/green] [bold]0.0.4[/bold]
[green]Author:[/green] Meet Solanki (AIML Student)
[green]Architecture:[/green] Modern OpenAI-based CLI
[green]Features:[/green] Multi-Provider • Rich UI • Streaming • File Analysis

[dim]🚀 The future of AI-powered development assistance![/dim]""",
        title="📦 Version Information",
        border_style="green"
    )
    console.print(version_panel)
async def async_main():
    """Main entry point with Rich CLI parsing"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    session_id = "default"
    workspace = "."

    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ['-h', '--help']:
            show_rich_help()
            return
            
        elif arg in ['-v', '--version']:
            show_rich_version()
            return
            
        elif arg in ['-s', '--session']:
            if i + 1 < len(args):
                session_id = args[i + 1]  
                i += 1
            else:
                console.print("[red]❌ Error: --session requires a value[/red]")
                return
                
        elif arg in ['-w', '--workspace']:
            if i + 1 < len(args):
                workspace = args[i + 1]
                i += 1
            else:
                console.print("[red]❌ Error: --workspace requires a value[/red]")
                return
                
        else:
            console.print(f"[red]❌ Unknown argument: {arg}[/red]")
            console.print("[yellow]💡 Use --help for usage information[/yellow]")
            return
            
        i += 1

    console.print()
    console.print(Panel.fit(
        "[bold blue]🤖 MaaHelper v0.0.4[/bold blue]\n"
        "[dim]Starting Modern Enhanced CLI...[/dim]\n"
        "👨‍💻 Created by Meet Solanki (AIML Student)",
        title="🚀 Initializing",
        border_style="blue"
    ))

    cli = create_cli(session_id, workspace)
    await cli.start()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()