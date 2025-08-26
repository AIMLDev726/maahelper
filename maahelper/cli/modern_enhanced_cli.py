"""
MaaHelper - Modern Enhanced CLI
Streamlined implementation using OpenAI client and Rich UI
"""

import asyncio
<<<<<<< HEAD
=======
import json
>>>>>>> 9a27ace (Initial commit)
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
<<<<<<< HEAD
from ..core.llm_client import UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models
from ..utils.streaming import ModernStreamingHandler, ConversationManager
from ..managers.streamlined_api_key_manager import api_key_manager
from ..utils.streamlined_file_handler import file_handler
=======
from ..core.llm_client import UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models, get_provider_models_dynamic
from ..utils.streaming import ModernStreamingHandler, ConversationManager
from ..managers.streamlined_api_key_manager import api_key_manager
from ..utils.streamlined_file_handler import file_handler
from ..workflows.commands import WorkflowCommands
from ..ide.commands import IDECommands
>>>>>>> 9a27ace (Initial commit)

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
<<<<<<< HEAD
=======

        # Initialize workflow and IDE commands
        self.workflow_commands: Optional[WorkflowCommands] = None
        self.ide_commands: Optional[IDECommands] = None
>>>>>>> 9a27ace (Initial commit)
        
        # Setup file handler
        file_handler.workspace_path = self.workspace_path
        
        # System prompt
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get enhanced system prompt"""
<<<<<<< HEAD
        return f"""You are MaaHelper v0.0.4 — a professional AI programming assistant developed by Meet Solanki (AIML Student). Your goal is to deliver accurate, context-aware coding help with intelligent file-level understanding.

== SYSTEM OVERVIEW ==
• Name        : MaaHelper v0.0.4
• Creator     : Meet Solanki (AIML Student)
• Objective   : Advanced programming assistance with workspace-level file processing
• Guiding Goal: Boost developer productivity through AI-powered problem-solving
=======
        # Import version safely
        try:
            from maahelper import __version__
        except ImportError:
            __version__ = "0.0.5"
        return f"""You are MaaHelper v{__version__} — a professional AI programming assistant developed by Meet Solanki (AIML Student). Your goal is to deliver accurate, context-aware coding help with intelligent file-level understanding, real-time analysis, and Git integration.

== SYSTEM OVERVIEW ==
• Name        : MaaHelper v{__version__}
• Creator     : Meet Solanki (AIML Student)
• Objective   : Advanced programming assistance with workspace-level file processing, real-time analysis, and Git integration
• Guiding Goal: Boost developer productivity through AI-powered problem-solving and workflow automation
>>>>>>> 9a27ace (Initial commit)

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
<<<<<<< HEAD
            console.print(Panel.fit(
                Align.center(
                    "[bold blue]🤖 MaaHelper v0.0.4[/bold blue]\n"
=======
            # Import version safely
            try:
                from maahelper import __version__
            except ImportError:
                __version__ = "0.0.5"
            console.print(Panel.fit(
                Align.center(
                    f"[bold blue]🤖 MaaHelper v{__version__}[/bold blue]\n"
>>>>>>> 9a27ace (Initial commit)
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
            
<<<<<<< HEAD
            # Model selection with Rich formatting  
            with console.status(f"[bold green]Loading models for {selected_provider.upper()}...", spinner="dots"):
                await asyncio.sleep(0.5)  # Brief pause for effect
                available_models = get_provider_models(selected_provider)
=======
            # Model selection with Rich formatting
            with console.status(f"[bold green]Loading models for {selected_provider.upper()}...", spinner="dots"):
                await asyncio.sleep(0.5)  # Brief pause for effect

                # Try to get API key for dynamic model fetching
                api_key = api_key_manager.get_api_key(selected_provider)

                if api_key:
                    # Try dynamic model fetching first
                    try:
                        available_models = await get_provider_models_dynamic(selected_provider, api_key)
                        if available_models:
                            console.print(f"[dim]✅ Fetched {len(available_models)} models dynamically[/dim]")
                        else:
                            available_models = get_provider_models(selected_provider)
                            console.print(f"[dim]📋 Using static model list[/dim]")
                    except Exception as e:
                        console.print(f"[dim]⚠ Dynamic fetch failed: {e}[/dim]")
                        available_models = get_provider_models(selected_provider)
                else:
                    # Fallback to static models
                    available_models = get_provider_models(selected_provider)
                    console.print(f"[dim]📋 Using static model list (no API key)[/dim]")
>>>>>>> 9a27ace (Initial commit)
            
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
<<<<<<< HEAD
                progress.update(task2, advance=50)
                progress.update(task3, advance=50)
=======

                # Initialize workflow and IDE commands
                task4 = progress.add_task("[green]Initializing workflows...", total=100)
                await asyncio.sleep(0.2)
                self.workflow_commands = WorkflowCommands(self.llm_client, str(self.workspace_path))
                progress.update(task4, advance=50)

                task5 = progress.add_task("[green]Initializing IDE integration...", total=100)
                await asyncio.sleep(0.2)
                self.ide_commands = IDECommands(self.llm_client)
                progress.update(task5, advance=50)

                progress.update(task2, advance=50)
                progress.update(task3, advance=50)
                progress.update(task4, advance=50)
                progress.update(task5, advance=50)
>>>>>>> 9a27ace (Initial commit)
            
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
<<<<<<< HEAD
        help_content = f"""
# 🤖 MaaHelper v0.0.4 - Modern Enhanced CLI

## 📝 Basic Commands
- `help` - Show this help message
- `exit`, `quit`, `bye` - Exit the application  
=======
        # Import version safely
        try:
            from maahelper import __version__
        except ImportError:
            __version__ = "0.0.5"
        help_content = f"""
# 🤖 MaaHelper v{__version__} - Advanced AI Coding Assistant

## 📝 Basic Commands
- `help` - Show this help message
- `exit`, `quit`, `bye` - Exit the application
>>>>>>> 9a27ace (Initial commit)
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
<<<<<<< HEAD

## 💡 Features
=======
- `discover-models` - Refresh and discover all available models

## 🆕 New Features (v{__version__})
### 🔍 Dynamic Model Discovery
- `discover-models` - Auto-discover latest models from all providers
- Real-time model availability with context length info

### 📊 Real-time Code Analysis
- `analyze-start` - Start watching files for real-time feedback
- `analyze-stop` - Stop real-time analysis
- `analyze-workspace` - Analyze entire workspace for issues

### 🔧 Git Integration
- `git-commit` - AI-generated smart commit messages
- `git-commit-auto` - Auto-stage and commit with AI messages
- `git-branch` - AI-suggested branch names

### 🤖 Custom Agent Prompts (Vibecoding)
- `prompts` - List all available custom prompts
- `prompt-categories` - Show prompt categories
- `code-review` - Comprehensive code review with AI
- `bug-analysis` - Deep bug analysis and solutions
- `architecture-design` - System architecture guidance
- `implement-feature` - Complete feature implementation
- `refactor-code` - Code refactoring assistance
- `explain-concept` - Programming concept explanations
- `optimize-performance` - Performance optimization analysis

### 🔄 Project-wide Workflows
- `workflow-templates` - List available workflow templates
- `workflow-create <template>` - Create workflow from template
- `workflow-list` - List all workflows
- `workflow-execute <id>` - Execute a workflow
- `workflow-status <id>` - Get workflow status
- `workflow-stats` - Get workflow statistics

### 🔧 IDE Integration
- `lsp-server` - Start Language Server Protocol server
- `lsp-server --port <port>` - Start LSP server on specific port
- `ide-analyze <file>` - Analyze file for IDE integration

## 💡 Core Features
>>>>>>> 9a27ace (Initial commit)
- **Real-time streaming** responses for immediate feedback
- **Multi-provider support** (OpenAI, Groq, Anthropic, Google, Ollama)
- **Intelligent file processing** with AI analysis
- **Rich formatting** with syntax highlighting
- **Persistent conversation** history per session
<<<<<<< HEAD
=======
- **Live code analysis** with error detection
- **Smart Git operations** with AI assistance
>>>>>>> 9a27ace (Initial commit)

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
    
<<<<<<< HEAD
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
            
=======
    async def process_command(self, user_input: str) -> tuple[bool, bool]:
        """Process special commands, return (should_exit, was_handled)"""
        command = user_input.lower().strip()

        if command in ['exit', 'quit', 'bye']:
            console.print("👋 [bold blue]Thank you for using MaaHelper![/bold blue]")
            console.print("[dim]Created by Meet Solanki (AIML Student)[/dim]")
            return True, True
            
        elif command == 'help':
            await self.show_help()
            return False, True

        elif command == 'clear':
            if self.conversation_manager:
                self.conversation_manager.clear_history()
            return False, True

        elif command == 'status':
            await self.show_status()
            return False, True

        elif command == 'files':
            file_handler.show_supported_files_table()
            return False, True

        elif command == 'files table':
            file_handler.show_supported_files_table()
            return False, True
            
        elif command == 'dir':
            file_handler.show_directory_structure(show_files=False)
            return False, True

>>>>>>> 9a27ace (Initial commit)
        elif command.startswith('file-search '):
            filepath = command[12:].strip()
            if not filepath:
                console.print("[red]Usage: file-search <filepath>[/red]")
<<<<<<< HEAD
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
=======
                return False, True

            await file_handler.file_search_command(filepath, self.llm_client)
            return False, True

        elif command == 'providers':
            providers = api_key_manager.get_available_providers()
            console.print(f"[green]Available providers:[/green] {', '.join(providers)}")
            return False, True
            
        elif command == 'models':
            # Use new dynamic model discovery
            with console.status(f"[bold green]Discovering models...", spinner="dots"):
                try:
                    from ..features.model_discovery import model_discovery
                    # Import version safely
                    try:
                        from maahelper import __version__
                    except ImportError:
                        __version__ = "0.0.5"
                    all_models = await model_discovery.get_available_models(self.current_provider)
                    if self.current_provider in all_models:
                        models = all_models[self.current_provider]
                        console.print(f"[green]✨ Models for {self.current_provider.upper()} (v{__version__} Dynamic Discovery):[/green]")
                        for model in models[:15]:
                            context_info = f" ({model.context_length:,} tokens)" if model.context_length > 0 else ""
                            console.print(f"  • {model.id}{context_info}")
                        if len(models) > 15:
                            console.print(f"  [dim]... and {len(models) - 15} more models[/dim]")
                    else:
                        console.print(f"[yellow]No models found for {self.current_provider}[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error discovering models: {e}[/red]")
            return False, True

        elif command == 'discover-models':
            # Force refresh all models
            with console.status("[bold green]Discovering all available models...", spinner="dots"):
                try:
                    from ..features.model_discovery import model_discovery
                    all_models = await model_discovery.get_available_models(force_refresh=True)
                    console.print("[green]✨ Model Discovery Complete![/green]")
                    for provider, models in all_models.items():
                        console.print(f"\n[cyan]{provider.upper()}:[/cyan] {len(models)} models")
                        for model in models[:5]:  # Show first 5 per provider
                            console.print(f"  • {model.id}")
                        if len(models) > 5:
                            console.print(f"  [dim]... and {len(models) - 5} more[/dim]")
                except Exception as e:
                    console.print(f"[red]Error discovering models: {e}[/red]")
            return False, True

        elif command == 'analyze-start':
            # Start real-time code analysis
            try:
                from ..features.realtime_analysis import realtime_analyzer
                if realtime_analyzer.is_running:
                    console.print("[yellow]Real-time analysis is already running. Restarting...[/yellow]")
                    realtime_analyzer.restart_watching(show_live_display=True)
                else:
                    realtime_analyzer.start_watching(show_live_display=True)
                console.print("[green]✨ Real-time code analysis started![/green]")
            except Exception as e:
                console.print(f"[red]Error starting analysis: {e}[/red]")
            return False, True

        elif command == 'analyze-stop':
            # Stop real-time code analysis
            try:
                from ..features.realtime_analysis import realtime_analyzer
                realtime_analyzer.stop_watching()
                console.print("[yellow]Real-time analysis stopped[/yellow]")
            except Exception as e:
                console.print(f"[red]Error stopping analysis: {e}[/red]")
            return False, True

        elif command == 'analyze-workspace':
            # Analyze entire workspace
            with console.status("[bold green]Analyzing workspace...", spinner="dots"):
                try:
                    from ..features.realtime_analysis import realtime_analyzer
                    results = await realtime_analyzer.analyze_workspace()
                    summary = realtime_analyzer.get_summary()
                    console.print(f"[green]✨ Workspace Analysis Complete![/green]")
                    console.print(f"Files analyzed: {summary.get('files_analyzed', 0)}")
                    console.print(f"Issues found: {summary.get('total_issues', 0)}")
                    console.print(f"Errors: {summary.get('errors', 0)}")
                    console.print(f"Warnings: {summary.get('warnings', 0)}")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "tool choice" in error_msg or "function" in error_msg:
                        console.print(f"[yellow]⚠️ Tool calling issue detected during analysis.[/yellow]")
                        console.print(f"[yellow]   This has been automatically handled. Analysis may continue.[/yellow]")
                        console.print(f"[dim]   Technical details: {e}[/dim]")
                    else:
                        console.print(f"[red]Error analyzing workspace: {e}[/red]")
                        console.print(f"[dim]If this is a tool-related error, it should be automatically handled.[/dim]")
            return False, True

        elif command == 'git-commit':
            # Smart Git commit
            try:
                from ..features.git_integration import git_integration
                success = await git_integration.smart_commit(self.llm_client, auto_stage=False)
                if success:
                    console.print("[green]✨ Smart commit completed![/green]")
                else:
                    console.print("[yellow]Commit cancelled or failed[/yellow]")
            except Exception as e:
                console.print(f"[red]Error with Git commit: {e}[/red]")
            return False, True

        elif command == 'git-commit-auto':
            # Smart Git commit with auto-staging
            try:
                from ..features.git_integration import git_integration
                success = await git_integration.smart_commit(self.llm_client, auto_stage=True)
                if success:
                    console.print("[green]✨ Smart commit with auto-staging completed![/green]")
                else:
                    console.print("[yellow]Commit cancelled or failed[/yellow]")
            except Exception as e:
                console.print(f"[red]Error with Git commit: {e}[/red]")
            return False, True

        elif command == 'git-branch':
            # Suggest branch name
            try:
                from ..features.git_integration import git_integration
                branch_name = await git_integration.suggest_branch_name_interactive()
                if branch_name:
                    console.print(f"[green]✨ Created branch: {branch_name}[/green]")
            except Exception as e:
                console.print(f"[red]Error with Git branch: {e}[/red]")
            return False, True

        elif command == 'prompts':
            # List all available custom prompts
            try:
                from ..vibecoding.prompts import vibecoding_prompts
                prompts = vibecoding_prompts.list_prompts()

                console.print("\n🤖 [bold cyan]Available Custom Agent Prompts:[/bold cyan]")
                for prompt in prompts:
                    console.print(f"  • [green]{prompt.name}[/green] - {prompt.description}")
                    console.print(f"    [dim]Category: {prompt.category}[/dim]")
                console.print(f"\n[dim]Total: {len(prompts)} custom prompts available[/dim]")
                console.print("[yellow]💡 Use 'prompt-categories' to see categories or try specific commands like 'code-review'[/yellow]")
            except Exception as e:
                console.print(f"[red]Error listing prompts: {e}[/red]")
            return False, True

        elif command == 'prompt-categories':
            # Show prompt categories
            try:
                from ..vibecoding.prompts import vibecoding_prompts
                categories = vibecoding_prompts.get_categories()

                console.print("\n📂 [bold cyan]Prompt Categories:[/bold cyan]")
                for category in categories:
                    prompts_in_category = vibecoding_prompts.list_prompts(category)
                    console.print(f"  • [green]{category.title()}[/green] ({len(prompts_in_category)} prompts)")
                    for prompt in prompts_in_category:
                        console.print(f"    - {prompt.name}")
            except Exception as e:
                console.print(f"[red]Error showing categories: {e}[/red]")
            return False, True

        elif command.startswith('code-review'):
            # AI-powered code review
            try:
                from ..vibecoding.commands import VibecodingCommands
                vibe_commands = VibecodingCommands(self.llm_client)

                # Get code from user
                code = Prompt.ask("📝 Enter code to review (or file path)")
                if code.endswith('.py') or code.endswith('.js') or code.endswith('.ts'):
                    # Try to read file
                    try:
                        with open(code, 'r') as f:
                            code_content = f.read()
                        language = code.split('.')[-1]
                    except:
                        console.print(f"[red]Could not read file: {code}[/red]")
                        return False, True
                else:
                    code_content = code
                    language = Prompt.ask("Programming language", default="python")

                context = Prompt.ask("Context/description (optional)", default="")
                focus_areas = Prompt.ask("Focus areas (optional)", default="")

                console.print("\n🔍 [cyan]Performing AI code review...[/cyan]")
                result = await vibe_commands.code_review(code_content, language, context, focus_areas)
                console.print(Panel(result, title="🤖 AI Code Review", border_style="green"))

            except Exception as e:
                console.print(f"[red]Error with code review: {e}[/red]")
            return False, True

        elif command.startswith('bug-analysis'):
            # AI-powered bug analysis
            try:
                from ..vibecoding.commands import VibecodingCommands
                vibe_commands = VibecodingCommands(self.llm_client)

                problem = Prompt.ask("🐛 Describe the problem/bug")
                code = Prompt.ask("📝 Enter problematic code")
                language = Prompt.ask("Programming language", default="python")
                error_details = Prompt.ask("Error message/details (optional)", default="")
                environment = Prompt.ask("Environment info (optional)", default="")

                console.print("\n🔍 [cyan]Analyzing bug...[/cyan]")
                result = await vibe_commands.bug_analysis(problem, code, language, error_details, environment)
                console.print(Panel(result, title="🐛 Bug Analysis & Solution", border_style="red"))

            except Exception as e:
                console.print(f"[red]Error with bug analysis: {e}[/red]")
            return False, True

        elif command.startswith('explain-concept'):
            # AI-powered concept explanation
            try:
                from ..vibecoding.commands import VibecodingCommands
                vibe_commands = VibecodingCommands(self.llm_client)

                concept = Prompt.ask("📚 What concept would you like explained?")
                context = Prompt.ask("Context/use case (optional)", default="")
                audience_level = Prompt.ask("Audience level", default="intermediate", choices=["beginner", "intermediate", "advanced"])
                questions = Prompt.ask("Specific questions (optional)", default="")

                console.print("\n🧠 [cyan]Explaining concept...[/cyan]")
                result = await vibe_commands.explain_concept(concept, context, audience_level, questions)
                console.print(Panel(result, title="📚 Concept Explanation", border_style="blue"))

            except Exception as e:
                console.print(f"[red]Error with concept explanation: {e}[/red]")
            return False, True

        elif command.startswith('optimize-performance'):
            # AI-powered performance optimization
            try:
                from ..vibecoding.commands import VibecodingCommands
                vibe_commands = VibecodingCommands(self.llm_client)

                code = Prompt.ask("📝 Enter code to optimize")
                language = Prompt.ask("Programming language", default="python")
                performance_issues = Prompt.ask("Known performance issues", default="")
                constraints = Prompt.ask("Constraints/requirements", default="")
                target_metrics = Prompt.ask("Target performance metrics", default="")
                environment = Prompt.ask("Environment details", default="")

                console.print("\n⚡ [cyan]Analyzing performance...[/cyan]")
                result = await vibe_commands.optimize_performance(code, language, performance_issues, constraints, target_metrics, environment)
                console.print(Panel(result, title="⚡ Performance Optimization", border_style="yellow"))

            except Exception as e:
                console.print(f"[red]Error with performance optimization: {e}[/red]")
            return False, True

        # Workflow Commands
        elif command == 'workflow-templates':
            # List workflow templates
            if self.workflow_commands:
                result = await self.workflow_commands.list_templates()
                console.print(result)
            else:
                console.print("[red]❌ Workflow system not initialized[/red]")
            return False, True

        elif command.startswith('workflow-create '):
            # Create workflow from template
            template_name = command[16:].strip()
            if self.workflow_commands:
                result = await self.workflow_commands.create_workflow_from_template(template_name)
                console.print(result)
            else:
                console.print("[red]❌ Workflow system not initialized[/red]")
            return False, True

        elif command == 'workflow-list':
            # List all workflows
            if self.workflow_commands:
                result = await self.workflow_commands.list_workflows()
                console.print(result)
            else:
                console.print("[red]❌ Workflow system not initialized[/red]")
            return False, True

        elif command.startswith('workflow-execute '):
            # Execute workflow
            workflow_id = command[17:].strip()
            if self.workflow_commands:
                result = await self.workflow_commands.execute_workflow(workflow_id)
                console.print(result)
            else:
                console.print("[red]❌ Workflow system not initialized[/red]")
            return False, True

        elif command.startswith('workflow-status '):
            # Get workflow status
            workflow_id = command[16:].strip()
            if self.workflow_commands:
                result = await self.workflow_commands.get_workflow_status(workflow_id)
                console.print(result)
            else:
                console.print("[red]❌ Workflow system not initialized[/red]")
            return False, True

        elif command == 'workflow-stats':
            # Get workflow statistics
            if self.workflow_commands:
                result = await self.workflow_commands.get_workflow_statistics()
                console.print(result)
            else:
                console.print("[red]❌ Workflow system not initialized[/red]")
            return False, True

        # IDE Integration Commands
        elif command == 'lsp-server':
            # Start LSP server
            if self.ide_commands:
                result = await self.ide_commands.start_lsp_server(stdio=True)
                console.print(result)
            else:
                console.print("[red]❌ IDE integration not initialized[/red]")
            return False, True

        elif command.startswith('lsp-server --port '):
            # Start LSP server on specific port
            try:
                port = int(command[18:].strip())
                if self.ide_commands:
                    result = await self.ide_commands.start_lsp_server(port=port)
                    console.print(result)
                else:
                    console.print("[red]❌ IDE integration not initialized[/red]")
            except ValueError:
                console.print("[red]❌ Invalid port number[/red]")
            return False, True

        elif command.startswith('ide-analyze '):
            # Analyze file for IDE
            file_path = command[12:].strip()
            if self.ide_commands:
                result = await self.ide_commands.analyze_for_ide(file_path)
                console.print(Panel(
                    json.dumps(result, indent=2),
                    title="🔍 IDE Analysis Result",
                    border_style="blue"
                ))
            else:
                console.print("[red]❌ IDE integration not initialized[/red]")
            return False, True

        return False, False  # Command not handled
>>>>>>> 9a27ace (Initial commit)
    
    async def main_loop(self):
        """Main interaction loop with Rich formatting"""
        console.print()
<<<<<<< HEAD
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
=======
        # Import version safely
        try:
            from maahelper import __version__
        except ImportError:
            __version__ = "0.0.5"
        welcome_panel = Panel.fit(
            Align.center(
                f"[bold green]🎉 MaaHelper v{__version__} Ready![/bold green]\n\n"
                "[yellow]💬 Start chatting or try these NEW commands:[/yellow]\n"
                "• [cyan]help[/cyan] - Show all commands\n"
                "• [cyan]prompts[/cyan] - 🆕 Custom AI agent prompts\n"
                "• [cyan]code-review[/cyan] - 🆕 AI-powered code review\n"
                "• [cyan]bug-analysis[/cyan] - 🆕 Deep bug analysis\n"
                "• [cyan]discover-models[/cyan] - Auto-discover latest AI models\n"
                "• [cyan]analyze-start[/cyan] - Real-time code analysis\n"
                "• [cyan]git-commit[/cyan] - AI-powered smart commits\n"
                "• [cyan]file-search <path>[/cyan] - Analyze any file with AI\n"
                "• [cyan]workflow-templates[/cyan] - 🆕 Project-wide workflows\n"
                "• [cyan]lsp-server[/cyan] - 🆕 IDE integration server\n"
                "• [cyan]status[/cyan] - Check current configuration\n\n"
                "[dim]✨ New: Project workflows, IDE integration & deep VSCode support![/dim]"
            ),
            title=f"✨ Welcome to MaaHelper v{__version__}",
>>>>>>> 9a27ace (Initial commit)
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
<<<<<<< HEAD
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
=======
                should_exit, was_handled = await self.process_command(user_input)
                if should_exit:
                    break

                # Only process as AI conversation if command was not handled
                if not was_handled:
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
>>>>>>> 9a27ace (Initial commit)
                    
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
<<<<<<< HEAD
    help_panel = Panel.fit(
        """[bold blue]🤖 MaaHelper v0.0.4[/bold blue]
=======
    # Import version safely
    try:
        from maahelper import __version__
    except ImportError:
        __version__ = "0.0.5"
    help_panel = Panel.fit(
        f"""[bold blue]🤖 MaaHelper v{__version__}[/bold blue]
>>>>>>> 9a27ace (Initial commit)
[dim]Modern Enhanced CLI with Multi-Provider Support[/dim]
👨‍💻 Created by Meet Solanki (AIML Student)

[bold green]🚀 USAGE:[/bold green]
<<<<<<< HEAD
  [cyan]python -m ai_helper_agent.cli.modern_enhanced_cli[/cyan] [OPTIONS]
=======
  [cyan]python -m maahelper.cli.modern_enhanced_cli[/cyan] [OPTIONS]
>>>>>>> 9a27ace (Initial commit)
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
<<<<<<< HEAD
  [cyan]python -m ai_helper_agent.cli.modern_enhanced_cli[/cyan]
  
  [dim]# Custom session and workspace[/dim]
  [cyan]ai-helper --session my_project --workspace /path/to/project[/cyan]
=======
  [cyan]python -m maahelper.cli.modern_enhanced_cli[/cyan]
  
  [dim]# Custom session and workspace[/dim]
  [cyan]maahelper --session my_project --workspace /path/to/project[/cyan]
>>>>>>> 9a27ace (Initial commit)

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
<<<<<<< HEAD
        title="🤖 MaaHelper v0.0.4 - Help",
=======
        title=f"🤖 MaaHelper v{__version__} - Help",
>>>>>>> 9a27ace (Initial commit)
        border_style="blue",
        padding=(1, 2)
    )
    console.print(help_panel)

def show_rich_version():
    """Show Rich-formatted version"""
<<<<<<< HEAD
    version_panel = Panel.fit(
        """[bold blue]🤖 MaaHelper[/bold blue]
[green]Version:[/green] [bold]0.0.4[/bold]
=======
    # Import version safely
    try:
        from maahelper import __version__
    except ImportError:
        __version__ = "0.0.5"
    version_panel = Panel.fit(
        f"""[bold blue]🤖 MaaHelper[/bold blue]
[green]Version:[/green] [bold]{__version__}[/bold]
>>>>>>> 9a27ace (Initial commit)
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

<<<<<<< HEAD
    console.print()
    console.print(Panel.fit(
        "[bold blue]🤖 MaaHelper v0.0.4[/bold blue]\n"
=======
    # Import version safely
    try:
        from maahelper import __version__
    except ImportError:
        __version__ = "0.0.5"
    console.print()
    console.print(Panel.fit(
        f"[bold blue]🤖 MaaHelper v{__version__}[/bold blue]\n"
>>>>>>> 9a27ace (Initial commit)
        "[dim]Starting Modern Enhanced CLI...[/dim]\n"
        "👨‍💻 Created by Meet Solanki (AIML Student)",
        title="🚀 Initializing",
        border_style="blue"
    ))

    cli = create_cli(session_id, workspace)
    await cli.start()

def main():
<<<<<<< HEAD
    asyncio.run(async_main())

=======
    """Main entry point for console scripts"""
    asyncio.run(async_main())

def cli_entry():
    """Entry point specifically for command-line usage"""
    # This function is called by the console script entry points
    main()

>>>>>>> 9a27ace (Initial commit)
if __name__ == "__main__":
    main()