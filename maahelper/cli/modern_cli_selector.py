"""
AI Helper Agent - Modern CLI Selector
Entry point to launch the modern OpenAI-based CLI system
"""

import os
import sys
import asyncio
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .modern_enhanced_cli import ModernEnhancedCLI
from ..managers.streamlined_api_key_manager import api_key_manager

console = Console()

class ModernCLISelector:
    """
    Modern CLI selector for OpenAI-based system.
    Entry point for launching the modern CLI, handling setup, provider status, workspace selection, and CLI launch.
    If no API key is found, automatically launch the API Key Manager for setup and re-check configuration.
    """
    
    def __init__(self):
        self.workspace_path = Path.cwd()
        
    def show_welcome(self):
        """Show welcome screen"""
        console.print()
        console.print(Panel.fit(
            "[bold blue]🤖 AI Helper Agent v0.0.4[/bold blue]\n"
            "[bold green]Modern OpenAI-Compatible CLI System[/bold green]\n\n"
            "✅ [cyan]Streamlined OpenAI client integration[/cyan]\n"
            "🚀 [cyan]Ultra-fast responses with streaming[/cyan]\n"
            "📁 [cyan]Intelligent file processing with AI analysis[/cyan]\n"
            "🔧 [cyan]Multi-provider support (OpenAI, Groq, Anthropic, Google, Ollama)[/cyan]\n"
            "🎨 [cyan]Rich UI with syntax highlighting[/cyan]\n\n"
            "[dim]👨‍💻 Created by Meet Solanki (AIML Student)[/dim]",
            title="🌟 Welcome to Modern AI Helper Agent",
            border_style="blue"
        ))
        console.print()
        
    def check_setup(self) -> bool:
        """
        Check if the system is properly set up.
        If no API key is found, automatically launch the API Key Manager for setup and re-check configuration.
        """
        # Check if any API keys are configured
        available = api_key_manager.get_available_providers()
        if not available:
            console.print(Panel.fit(
                "[bold red]⚠️ Setup Required[/bold red]\n\n"
                "[bold red]⚠️ For Free Ollama Models apikey provide random text like like abc,xyz,etc ...[/bold red]\n\n"
                "[yellow]No API keys found. The system needs at least one API key to function.[/yellow]\n\n"
                "[cyan]Launching API Key Manager for setup...[/cyan]",
                title="🔑 API Key Setup Required",
                border_style="red"
            ))
            # Launch API Key Manager interactive menu
            try:
                from ..managers.advanced_api_key_manager import advanced_api_key_manager
                advanced_api_key_manager.interactive_menu()
            except Exception as e:
                console.print(f"[red]❌ Failed to launch API Key Manager: {e}[/red]")
            # Re-check after setup
            available = api_key_manager.get_available_providers()
            if not available:
                console.print("[red]❌ No API keys configured. Please set up at least one API key to continue.[/red]")
                return False
        return True
    
    def show_available_providers(self):
        """Show available providers and their status"""
        # Dynamically fetch supported providers from PROVIDER_CONFIGS
        supported_providers = [
        'openai',
        'groq',
        'anthropic',
        'google',
        'ollama',
        'together',
        'fireworks',
        'openrouter',
        'localai',
        'deepinfra',
        'perplexity',
        'cerebras'
    ]

        available = api_key_manager.get_available_providers()

        table = Table(
            title="🔑 API Provider Status",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Provider", style="cyan", width=15)
        table.add_column("Status", style="white", width=10)
        table.add_column("Description", style="dim", width=50)

        descriptions = {
            'groq': 'Ultra-fast inference, great for coding tasks',
            'openai': 'GPT models, excellent general capabilities',
            'anthropic': 'Claude models, strong reasoning abilities',
            'google': 'Gemini models, multimodal capabilities',
            'ollama': 'Local models, runs on your machine',
            'together': 'Free access to open-source models via Together AI',
            'fireworks': 'Inference platform supporting Mistral & StableCode',
            'openrouter': 'Unified proxy for popular AI model endpoints',
            'localai': 'Self-hosted OpenAI-compatible inference API',
            'deepinfra': 'Cloud-based fast inference for open models',
            'perplexity': 'Perplexity RAG-based chat and R1 engine',
            'cerebras': 'Cerebras Wafer-Scale inference for LLaMA/Command'
        }

        for provider in supported_providers:
            status = "✅ Ready" if provider in available else "❌ No Key"
            description = descriptions.get(provider, "No description available")
            table.add_row(provider.upper(), status, description)

        console.print()
        console.print(table)
        console.print()

        
    def select_workspace(self) -> Path:
        """Allow user to select workspace directory"""
        console.print(f"[cyan]Current workspace:[/cyan] {self.workspace_path}")
        
        if Confirm.ask("Would you like to change the workspace directory?", default=False):
            while True:
                workspace_input = Prompt.ask("Enter workspace path", default=str(self.workspace_path))
                new_workspace = Path(workspace_input).resolve()
                
                if new_workspace.exists() and new_workspace.is_dir():
                    self.workspace_path = new_workspace
                    console.print(f"[green]✅ Workspace set to: {self.workspace_path}[/green]")
                    break
                else:
                    console.print(f"[red]❌ Directory does not exist: {new_workspace}[/red]")
                    if not Confirm.ask("Try again?", default=True):
                        break
        
        return self.workspace_path
    
    async def launch_modern_cli(self):
        """Launch the modern enhanced CLI"""
        console.print()
        console.print(Panel.fit(
            "[bold green]🚀 Launching Modern Enhanced CLI[/bold green]\n"
            "[cyan]Features:[/cyan] OpenAI client, File processing, Streaming, Multi-provider",
            title="Starting AI Helper Agent",
            border_style="green"
        ))
        
        # Create and start the modern CLI
        cli = ModernEnhancedCLI(workspace_path=str(self.workspace_path))
        await cli.start()
    
    async def run(self):
        """Main run method"""
        try:
            # Show welcome
            self.show_welcome()
            
            # Check setup
            if not self.check_setup():
                console.print("[yellow]Please configure API keys and try again.[/yellow]")
                return
            
            # Show provider status
            self.show_available_providers()
            
            # Select workspace
            self.select_workspace()
            
            # Launch the CLI
            await self.launch_modern_cli()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")


async def main():
    """Main entry point"""
    selector = ModernCLISelector()
    await selector.run()


def cli_selector_entry():
    """Entry point for CLI selector command"""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
