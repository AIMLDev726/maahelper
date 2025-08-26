"""
Advanced API Key Manager for AI Helper Agent v0.0.4
Secure local storage in C:/Users/{username}/.maahelper/
With Rich UI for password-protected management
"""

import os
import json
import getpass
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

console = Console()

class AdvancedAPIKeyManager:
    """Advanced API Key Manager with Rich UI and secure local storage"""
    
    def __init__(self):
        # Create ~/.maahelper directory in user's home
        self.config_dir = Path.home() / ".maahelper"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "keyring.key"
        
        # Ensure directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize encryption
        self.fernet = None
        self.is_unlocked = False
        
        self.providers = {
    "openai": {
        "name": "OpenAI",
        "env_var": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "free": False,
        "description": "Official GPT-3.5 / GPT-4 API"
    },
    "groq": {
        "name": "Groq",
        "env_var": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "free": True,
        "description": "Ultra-fast inference with LLaMA / Mixtral"
    },
    "together": {
        "name": "Together AI",
        "env_var": "TOGETHER_API_KEY",
        "base_url": "https://api.together.xyz/v1",
        "free": True,
        "description": "Free/Open access to Mistral, LLaMA, Mixtral etc"
    },
    "fireworks": {
        "name": "Fireworks AI",
        "env_var": "FIREWORKS_API_KEY",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "free": True,
        "description": "Supports Mistral and stable models"
    },
    "openrouter": {
        "name": "OpenRouter",
        "env_var": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "free": True,
        "description": "Unified gateway to multiple model providers"
    },
    "ollama": {
        "name": "Ollama",
        "env_var": "OLLAMA_BASE_URL",
        "base_url": "http://localhost:11434/v1",
        "free": True,
        "description": "Run local models with OpenAI-compatible API"
    },
    "localai": {
        "name": "LocalAI",
        "env_var": "LOCALAI_API_KEY",
        "base_url": "http://localhost:8080/v1",
        "free": True,
        "description": "Self-hosted OpenAI-compatible API"
    },
    "deepinfra": {
        "name": "DeepInfra",
        "env_var": "DEEPINFRA_API_KEY",
        "base_url": "https://api.deepinfra.com/v1/openai",
        "free": True,
        "description": "Supports Mistral, LLaMA models with good speed"
    },
    "perplexity": {
        "name": "Perplexity AI",
        "env_var": "PERPLEXITY_API_KEY",
        "base_url": "https://api.perplexity.ai/chat/completions",
        "free": False,
        "description": "R1 and mix models via OpenRouter compatible"
    },
    "cerebras": {
        "name": "Cerebras",
        "env_var": "CEREBRAS_API_KEY",
        "base_url": "https://api.cerebras.ai/v1",
        "free": True,
        "description": "Inference on Cerebras Wafer-Scale Engine, supports command and llama models"
    }
}

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _setup_encryption(self, password: str) -> bool:
        """Setup encryption with password"""
        try:
            if self.key_file.exists():
                # Load existing salt
                with open(self.key_file, 'rb') as f:
                    salt = f.read()
            else:
                # Create new salt
                salt = os.urandom(16)
                with open(self.key_file, 'wb') as f:
                    f.write(salt)
            
            key = self._derive_key(password, salt)
            self.fernet = Fernet(key)
            self.is_unlocked = True
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Encryption setup failed: {e}[/red]")
            return False
    
    def _load_config(self) -> Dict:
        """Load encrypted configuration"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            console.print(f"[red]❌ Failed to load config: {e}[/red]")
            return {}
    
    def _save_config(self, config: Dict) -> bool:
        """Save encrypted configuration"""
        try:
            json_data = json.dumps(config, indent=2)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to save config: {e}[/red]")
            return False
    
    def show_welcome(self):
        """Show beautiful welcome screen"""
        console.print()
        welcome_panel = Panel.fit(
            Align.center(
                "[bold blue]🔐 AI Helper Agent - API Key Manager[/bold blue]\n\n"
                "[green]Secure Local Storage:[/green]\n"
                f"📁 {self.config_dir}\n\n"
                "[yellow]Features:[/yellow]\n"
                "• 🔒 Password-protected encryption\n"
                "• 🎨 Rich UI management\n"
                "• 🔑 Multi-provider support\n"
                "• ✨ Easy setup and editing\n\n"
                "[dim]👨‍💻 Created by Meet Solanki (AIML Student)[/dim]"
            ),
            title="🚀 Welcome",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(welcome_panel)
    
    def unlock_keyring(self) -> bool:
        """Unlock the keyring with password"""
        if self.is_unlocked:
            return True
        
        # First time setup
        if not self.config_file.exists():
            console.print()
            console.print(Panel.fit(
                "[yellow]👋 First time setup![/yellow]\n"
                "Create a master password to secure your API keys.\n"
                "[dim]This password will encrypt all your API keys locally.[/dim]",
                title="🔐 Setup Required",
                border_style="yellow"
            ))
            
            while True:
                password = getpass.getpass("Create master password: ")
                if len(password) < 6:
                    console.print("[red]❌ Password must be at least 6 characters[/red]")
                    continue
                    
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    console.print("[red]❌ Passwords don't match[/red]")
                    continue
                    
                break
        else:
            # Existing setup
            console.print()
            console.print(Panel.fit(
                "[green]🔓 Enter your master password to unlock API keys[/green]",
                title="🔐 Authentication Required", 
                border_style="green"
            ))
            password = getpass.getpass("Master password: ")
        
        return self._setup_encryption(password)
    
    def show_provider_info(self):
        """Show available providers with Rich formatting"""
        console.print()
        console.print(Panel.fit(
            "[bold green]🤖 Supported AI Providers[/bold green]",
            border_style="green"
        ))
        
        # Create table
        table = Table(title="Available Providers", show_header=True, header_style="bold magenta")
        table.add_column("Provider", style="cyan", width=12)
        table.add_column("Free", style="green", width=6)
        table.add_column("Description", style="white", width=50)
        table.add_column("Setup URL", style="blue", width=30)
        
        for provider_id, info in self.providers.items():
            free_status = "✅ Yes" if info["free"] else "💳 Paid"
            table.add_row(
                info["name"],
                free_status,
                info["description"],
    info.get("base_url", "N/A")  # ✅ Uses base_url safely
            )
        
        console.print(table)
        console.print()
    
    def show_current_keys(self):
        """Show currently stored API keys"""
        if not self.unlock_keyring():
            return
        
        config = self._load_config()
        api_keys = config.get("api_keys", {})
        
        console.print()
        if not api_keys:
            console.print(Panel.fit(
                "[yellow]📝 No API keys stored yet[/yellow]\n"
                "Use 'add' command to add your first API key.",
                title="🔑 API Keys",
                border_style="yellow"
            ))
            return
        
        # Create table for stored keys
        table = Table(title="🔑 Stored API Keys", show_header=True, header_style="bold green")
        table.add_column("Provider", style="cyan", width=15)
        table.add_column("Status", style="green", width=10) 
        table.add_column("Key Preview", style="dim", width=20)
        table.add_column("Added", style="blue", width=20)
        
        for provider, key_data in api_keys.items():
            if isinstance(key_data, dict):
                key_preview = key_data.get("key", "")[:8] + "..." if key_data.get("key") else ""
                added_date = key_data.get("added", "Unknown")
            else:
                key_preview = str(key_data)[:8] + "..." if key_data else ""
                added_date = "Legacy"
            
            status = "✅ Active" if key_preview else "❌ Empty"
            table.add_row(
                provider.upper(),
                status,
                key_preview,
                added_date
            )
        
        console.print(table)
        console.print()
    
    def add_api_key(self, provider: str = None):
        """Add or update API key with Rich UI"""
        if not self.unlock_keyring():
            return
        
        # Show provider info first
        self.show_provider_info()
        
        # Provider selection
        if not provider:
            console.print("[bold]Select a provider to add/update:[/bold]")
            providers_list = list(self.providers.keys())
            for i, p in enumerate(providers_list, 1):
                console.print(f"  [cyan]{i}.[/cyan] {self.providers[p]['name']}")
            
            while True:
                try:
                    choice = Prompt.ask("Enter choice (1-10)", default="1")
                    idx = int(choice) - 1
                    if 0 <= idx < len(providers_list):
                        provider = providers_list[idx]
                        break
                    else:
                        console.print("[red]Invalid choice. Try again.[/red]")
                except ValueError:
                    console.print("[red]Please enter a number.[/red]")
        
        provider_info = self.providers.get(provider)
        if not provider_info:
            console.print(f"[red]❌ Unknown provider: {provider}[/red]")
            return
        
        # Show provider details
        console.print()
        console.print(Panel.fit(
            f"[bold blue]🔑 Adding API Key for {provider_info['name']}[/bold blue]\n\n"
            f"[yellow]Description:[/yellow] {provider_info['description']}\n"
            f"[yellow]Get your key:[/yellow] {provider_info['base_url']}\n"
            f"[yellow]Environment variable:[/yellow] {provider_info['env_var']}\n\n"
            "[dim]💡 Your API key will be encrypted and stored locally[/dim]",
            title="🚀 Setup",
            border_style="blue"
        ))
        
        # Get API key
        api_key = getpass.getpass(f"Enter your {provider_info['name']} API key: ")
        
        if not api_key.strip():
            console.print("[red]❌ Empty API key provided[/red]")
            return
        
        # Validate key format (basic check)
        if provider == "openai" and not api_key.startswith("sk-"):
            console.print("[yellow]⚠️ OpenAI keys usually start with 'sk-'[/yellow]")
            if not Confirm.ask("Continue anyway?"):
                return
        elif provider == "groq" and not api_key.startswith("gsk_"):
            console.print("[yellow]⚠️ Groq keys usually start with 'gsk_'[/yellow]")
            if not Confirm.ask("Continue anyway?"):
                return
        
        # Save key
        config = self._load_config()
        if "api_keys" not in config:
            config["api_keys"] = {}
        
        config["api_keys"][provider] = {
            "key": api_key,
            "added": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "provider": provider_info["name"]
        }
        
        if self._save_config(config):
            console.print()
            console.print(Panel.fit(
                f"[bold green]✅ {provider_info['name']} API key saved successfully![/bold green]\n"
                "[dim]Your key is encrypted and stored locally[/dim]",
                title="🎉 Success",
                border_style="green"
            ))
        else:
            console.print("[red]❌ Failed to save API key[/red]")
    
    def remove_api_key(self, provider: str = None):
        """Remove API key with confirmation"""
        if not self.unlock_keyring():
            return
        
        config = self._load_config()
        api_keys = config.get("api_keys", {})
        
        if not api_keys:
            console.print("[yellow]📝 No API keys to remove[/yellow]")
            return
        
        # Provider selection
        if not provider:
            console.print("[bold]Select a provider to remove:[/bold]")
            stored_providers = list(api_keys.keys())
            for i, p in enumerate(stored_providers, 1):
                provider_name = self.providers.get(p, {}).get("name", p.upper())
                console.print(f"  [cyan]{i}.[/cyan] {provider_name}")
            
            while True:
                try:
                    choice = Prompt.ask("Enter choice", default="1")
                    idx = int(choice) - 1
                    if 0 <= idx < len(stored_providers):
                        provider = stored_providers[idx]
                        break
                    else:
                        console.print("[red]Invalid choice. Try again.[/red]")
                except ValueError:
                    console.print("[red]Please enter a number.[/red]")
        
        if provider not in api_keys:
            console.print(f"[red]❌ No API key found for {provider}[/red]")
            return
        
        provider_name = self.providers.get(provider, {}).get("name", provider.upper())
        
        # Confirmation
        if Confirm.ask(f"Remove API key for {provider_name}?"):
            del config["api_keys"][provider]
            if self._save_config(config):
                console.print(f"[green]✅ {provider_name} API key removed[/green]")
            else:
                console.print("[red]❌ Failed to remove API key[/red]")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider (check environment first, then local storage)"""
        # Check environment variables first
        env_var = self.providers.get(provider, {}).get("env_var")
        if env_var:
            env_key = os.getenv(env_var)
            if env_key:
                return env_key
        
        # Check local storage
        if not self.is_unlocked:
            if not self.unlock_keyring():
                return None
        
        config = self._load_config()
        api_keys = config.get("api_keys", {})
        key_data = api_keys.get(provider)
        
        if isinstance(key_data, dict):
            return key_data.get("key")
        elif isinstance(key_data, str):
            return key_data
        
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of providers with available API keys"""
        available = []
        
        for provider in self.providers.keys():
            if self.get_api_key(provider):
                available.append(provider)
        
        return available
    
    def interactive_menu(self):
        """Interactive Rich UI menu"""
        self.show_welcome()
        
        while True:
            console.print()
            menu_panel = Panel.fit(
                "[bold blue]🔧 API Key Manager Menu[/bold blue]\n\n"
                "[cyan]1.[/cyan] 👀 View stored API keys\n"
                "[cyan]2.[/cyan] ➕ Add/Update API key\n" 
                "[cyan]3.[/cyan] ❌ Remove API key\n"
                "[cyan]4.[/cyan] 📋 Show provider info\n"
                "[cyan]5.[/cyan] 🚪 Exit\n",
                title="🎛️ Menu",
                border_style="blue"
            )
            console.print(menu_panel)
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="1")
            
            if choice == "1":
                self.show_current_keys()
            elif choice == "2":
                self.add_api_key()
            elif choice == "3":
                self.remove_api_key()
            elif choice == "4":
                self.show_provider_info()
            elif choice == "5":
                console.print()
                console.print(Panel.fit(
                    "[bold blue]👋 Thanks for using AI Helper Agent![/bold blue]\n"
                    "[dim]Your API keys are safely encrypted and stored locally[/dim]",
                    title="🔐 Goodbye",
                    border_style="blue"
                ))
                break


# Global instance
advanced_api_key_manager = AdvancedAPIKeyManager()


def main():
    """Main entry point for API key manager"""
    try:
        advanced_api_key_manager.interactive_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


if __name__ == "__main__":
    main()
