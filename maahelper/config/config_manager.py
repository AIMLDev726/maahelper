#!/usr/bin/env python3
"""
Configuration Management System
Centralized configuration with YAML/JSON support, environment variables, and validation
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from rich.console import Console

console = Console()


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider"""
    name: str
    base_url: str
    models: List[str] = field(default_factory=list)
    api_key_env: str = ""
    default_model: str = ""
    max_tokens: int = 2000
    temperature: float = 0.0
    timeout: int = 30


@dataclass
class UIConfig:
    """UI and display configuration"""
    theme: str = "dark"
    show_timestamps: bool = True
    show_token_count: bool = True
    max_history_display: int = 50
    animation_speed: float = 0.1


@dataclass
class SecurityConfig:
    """Security and privacy configuration"""
    encrypt_api_keys: bool = True
    log_requests: bool = False
    mask_sensitive_data: bool = True
    session_timeout: int = 3600


@dataclass
class PerformanceConfig:
    """Performance and optimization configuration"""
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    cache_responses: bool = True
    cache_ttl: int = 300


@dataclass
class FileHandlerConfig:
    """File handling configuration"""
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.html', '.css', '.json', '.yaml', '.md', '.txt'
    ])
    max_depth: int = 3
    exclude_patterns: List[str] = field(default_factory=lambda: [
        '__pycache__', '.git', '.vscode', 'node_modules', '.pytest_cache'
    ])


@dataclass
class AppConfig:
    """Main application configuration"""
    # Core settings
    app_name: str = "MaaHelper"
    version: str = "0.0.5"
    debug: bool = False
    log_level: str = "INFO"
    
    # Component configurations
    llm_providers: Dict[str, LLMProviderConfig] = field(default_factory=dict)
    ui: UIConfig = field(default_factory=UIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    file_handler: FileHandlerConfig = field(default_factory=FileHandlerConfig)
    
    # Paths
    config_dir: str = ""
    workspace_path: str = "."
    log_file: str = ""


class ConfigManager:
    """Centralized configuration management with validation and environment support"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = self._get_config_dir(config_dir)
        self.config_file = self.config_dir / "config.yaml"
        self.config: AppConfig = AppConfig()
        self._load_default_providers()
        
    def _get_config_dir(self, config_dir: Optional[str]) -> Path:
        """Get configuration directory with environment variable support"""
        if config_dir:
            return Path(config_dir).expanduser().resolve()
        
        # Check environment variable
        env_config_dir = os.getenv('MAAHELPER_CONFIG_DIR')
        if env_config_dir:
            return Path(env_config_dir).expanduser().resolve()
        
        # Default to user home directory
        return Path.home() / ".maahelper"
    
    def _load_default_providers(self) -> None:
        """Load default LLM provider configurations"""
        default_providers = {
            "openai": LLMProviderConfig(
                name="openai",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
                api_key_env="OPENAI_API_KEY",
                default_model="gpt-4o-mini"
            ),
            "anthropic": LLMProviderConfig(
                name="anthropic",
                base_url="https://api.anthropic.com/v1",
                models=["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
                api_key_env="ANTHROPIC_API_KEY",
                default_model="claude-3-5-sonnet-20241022"
            ),
            "groq": LLMProviderConfig(
                name="groq",
                base_url="https://api.groq.com/openai/v1",
                models=["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                api_key_env="GROQ_API_KEY",
                default_model="llama-3.1-70b-versatile"
            ),
            "google": LLMProviderConfig(
                name="google",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                models=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
                api_key_env="GOOGLE_API_KEY",
                default_model="gemini-1.5-flash"
            )
        }
        
        self.config.llm_providers = default_providers
    
    def load_config(self) -> AppConfig:
        """Load configuration from file with environment variable overrides"""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load from file if exists
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.suffix.lower() == '.yaml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                # Update config with loaded data
                self._update_config_from_dict(config_data)
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
            # Set computed paths
            self.config.config_dir = str(self.config_dir)
            if not self.config.log_file:
                self.config.log_file = str(self.config_dir / "maahelper.log")
            
            console.print(f"[green]✅ Configuration loaded from {self.config_file}[/green]")
            return self.config
            
        except Exception as e:
            console.print(f"[yellow]⚠ Error loading config: {e}. Using defaults.[/yellow]")
            return self.config
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict
            config_dict = asdict(self.config)
            
            # Save as YAML for better readability
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            console.print(f"[green]✅ Configuration saved to {self.config_file}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error saving config: {e}[/red]")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary data"""
        # Update basic fields
        for key, value in config_data.items():
            if hasattr(self.config, key) and not isinstance(getattr(self.config, key), dict):
                setattr(self.config, key, value)
        
        # Update nested configurations
        if 'ui' in config_data:
            self._update_dataclass(self.config.ui, config_data['ui'])
        
        if 'security' in config_data:
            self._update_dataclass(self.config.security, config_data['security'])
        
        if 'performance' in config_data:
            self._update_dataclass(self.config.performance, config_data['performance'])
        
        if 'file_handler' in config_data:
            self._update_dataclass(self.config.file_handler, config_data['file_handler'])
        
        # Update provider configurations
        if 'llm_providers' in config_data:
            for provider_name, provider_data in config_data['llm_providers'].items():
                if provider_name in self.config.llm_providers:
                    self._update_dataclass(self.config.llm_providers[provider_name], provider_data)
    
    def _update_dataclass(self, obj: Any, data: Dict[str, Any]) -> None:
        """Update dataclass object with dictionary data"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        # Debug mode
        if os.getenv('MAAHELPER_DEBUG'):
            self.config.debug = os.getenv('MAAHELPER_DEBUG').lower() in ('true', '1', 'yes')
        
        # Log level
        if os.getenv('MAAHELPER_LOG_LEVEL'):
            self.config.log_level = os.getenv('MAAHELPER_LOG_LEVEL').upper()
        
        # Workspace path
        if os.getenv('MAAHELPER_WORKSPACE'):
            self.config.workspace_path = os.getenv('MAAHELPER_WORKSPACE')
    
    def get_provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        """Get configuration for a specific provider"""
        return self.config.llm_providers.get(provider_name)
    
    def update_provider_config(self, provider_name: str, config: LLMProviderConfig) -> None:
        """Update configuration for a specific provider"""
        self.config.llm_providers[provider_name] = config
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate provider configurations
        for provider_name, provider_config in self.config.llm_providers.items():
            if not provider_config.base_url:
                issues.append(f"Provider {provider_name} missing base_url")
            
            if not provider_config.models:
                issues.append(f"Provider {provider_name} has no models configured")
        
        # Validate paths
        if not Path(self.config.workspace_path).exists():
            issues.append(f"Workspace path does not exist: {self.config.workspace_path}")
        
        return issues


# Global configuration manager instance
config_manager = ConfigManager()
