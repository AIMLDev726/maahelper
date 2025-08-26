"""
MaaHelper - Modern Enhanced CLI Package
Version 0.0.4 - Streamlined with OpenAI client integration
Created by Meet Solanki (AIML Student)

A comprehensive AI-powered programming assistant with advanced code generation,
analysis, debugging, and optimization capabilities using multiple LLM providers.

Modern Features:
- Unified OpenAI client for all providers (Groq, OpenAI, Anthropic, Google, Ollama)
- Real-time streaming responses with Rich UI
- Intelligent file processing and analysis
- Secure API key management without getpass
- Modern CLI with enhanced UX
- File-search command for AI-powered file analysis
- Multi-provider support with automatic model selection
- Async/await architecture for better performance
- Rich formatting with syntax highlighting
- Persistent conversation history

Key Components:
- UnifiedLLMClient: Single interface for all AI providers
- ModernStreamingHandler: Real-time response streaming
- StreamlinedAPIKeyManager: Environment-based key management
- StreamlinedFileHandler: AI-powered file analysis
- ModernEnhancedCLI: Main CLI interface

Usage:
    # Direct CLI usage
    from maahelper.cli.modern_enhanced_cli import main
    import asyncio
    asyncio.run(main())

    # Or programmatic usage
    from maahelper import create_cli
    cli = create_cli()
    await cli.start()
"""

# Modern components
from .core.llm_client import (
    UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models, get_provider_models_dynamic,
    LLMClientError, LLMConnectionError, LLMAuthenticationError, LLMRateLimitError, LLMModelError, LLMStreamingError
)

# Configuration and utilities
from .config.config_manager import config_manager
from .utils.input_validator import input_validator
from .utils.memory_manager import memory_manager
from .utils.rate_limiter import global_rate_limiter
from .utils.logging_system import get_logger

# New features (v0.0.5) - Import lazily to avoid circular imports
def get_model_discovery():
    from .features.model_discovery import model_discovery
    return model_discovery

def get_realtime_analyzer():
    from .features.realtime_analysis import realtime_analyzer
    return realtime_analyzer

def get_git_integration():
    from .features.git_integration import git_integration
    return git_integration

# Core utilities (safe to import)
from .utils.streaming import ModernStreamingHandler, ConversationManager
from .managers.streamlined_api_key_manager import api_key_manager
from .utils.streamlined_file_handler import file_handler

# CLI (import lazily)
def get_cli():
    from .cli.modern_enhanced_cli import ModernEnhancedCLI, create_cli
    return ModernEnhancedCLI, create_cli

# Version info
__version__ = "0.0.5"
__author__ = "Meet Solanki (AIML Student)"
__email__ = "aistudentlearn4@gmail.com"

# Package metadata
__title__ = "maahelper"
__description__ = "MaaHelper - Advanced AI-powered coding assistant with real-time analysis and Git integration"
__url__ = "https://github.com/AIMLDev726/maahelper"
__license__ = "MIT"

# Modern exports
__all__ = [
    # Core LLM functionality
    "UnifiedLLMClient",
    "create_llm_client",
    "get_all_providers",
    "get_provider_models",
    "get_provider_models_dynamic",

    # Exception classes
    "LLMClientError",
    "LLMConnectionError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelError",
    "LLMStreamingError",

    # Configuration management
    "config_manager",

    # Utilities
    "input_validator",
    "memory_manager",
    "global_rate_limiter",
    "get_logger",

    # New features (v0.0.5) - Lazy loading functions
    "get_model_discovery",
    "get_realtime_analyzer",
    "get_git_integration",
    "get_cli",
    
    # Streaming and conversation
    "ModernStreamingHandler",
    "ConversationManager",
    
    # Managers
    "api_key_manager",
    "file_handler",
    
    # CLI
    "ModernEnhancedCLI",
    "create_cli",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__"
]