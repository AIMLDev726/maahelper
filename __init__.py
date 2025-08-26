"""
MaaHelper - Advanced AI-powered coding assistant
Version 0.0.5 - With IDE Integration and Project-wide Workflows
Created by Meet Solanki (AIML Student)

A comprehensive AI-powered programming assistant with advanced code generation,
analysis, debugging, and optimization capabilities using multiple LLM providers.

Modern Features:
- Unified LLM client for all providers (Groq, OpenAI, Anthropic, Google, Ollama)
- Real-time streaming responses with Rich UI
- Deep IDE integration with VSCode extension and LSP server
- Project-wide agent workflows with LangGraph-inspired orchestration
- Intelligent file processing and analysis
- Secure API key management
- Modern CLI with enhanced UX
- Multi-provider support with automatic model selection
- Async/await architecture for better performance
- Rich formatting with syntax highlighting
- Persistent conversation history and workflow state

Key Components:
- UnifiedLLMClient: Single interface for all AI providers
- ModernStreamingHandler: Real-time response streaming
- StreamlinedAPIKeyManager: Environment-based key management
- StreamlinedFileHandler: AI-powered file analysis
- ModernEnhancedCLI: Main CLI interface
- WorkflowEngine: Project-wide workflow orchestration
- LSP Server: Language Server Protocol for IDE integration

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
from .maahelper.core.llm_client import (
    UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models, get_provider_models_dynamic,
    LLMClientError, LLMConnectionError, LLMAuthenticationError, LLMRateLimitError, LLMModelError, LLMStreamingError
)
from .maahelper.utils.streaming import ModernStreamingHandler, ConversationManager
from .maahelper.managers.streamlined_api_key_manager import api_key_manager
from .maahelper.utils.streamlined_file_handler import file_handler

# CLI (import lazily)
def get_cli():
    from .maahelper.cli.modern_enhanced_cli import ModernEnhancedCLI, create_cli
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

    # Exceptions
    "LLMClientError",
    "LLMConnectionError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelError",
    "LLMStreamingError",

    # Streaming and conversation
    "ModernStreamingHandler",
    "ConversationManager",

    # Managers
    "api_key_manager",
    "file_handler",

    # CLI
    "get_cli",

    # Metadata
    "__version__",
    "__author__",
    "__description__"
]