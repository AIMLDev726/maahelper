"""
AI Helper Agent - Modern Enhanced CLI Package
Version 0.0.3 - Streamlined with OpenAI client integration
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
    from ai_helper_agent.cli.modern_enhanced_cli import main
    import asyncio
    asyncio.run(main())
    
    # Or programmatic usage
    from ai_helper_agent import create_cli
    cli = create_cli()
    await cli.start()
"""

# Modern components
from .core.llm_client import UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models
from .utils.streaming import ModernStreamingHandler, ConversationManager
from .managers.streamlined_api_key_manager import api_key_manager
from .utils.streamlined_file_handler import file_handler
from .cli.modern_enhanced_cli import ModernEnhancedCLI, create_cli

# Version info
__version__ = "0.0.3"
__author__ = "Meet Solanki (AIML Student)"
__email__ = "aistudentlearn4@gmail.com"

# Package metadata
__title__ = "ai-helper-agent"
__description__ = "Modern AI Helper Agent with OpenAI client integration and multi-provider support"
__url__ = "https://github.com/AIMLDev726/ai-helper-agent"
__license__ = "MIT"

# Modern exports
__all__ = [
    # Core LLM functionality
    "UnifiedLLMClient",
    "create_llm_client", 
    "get_all_providers",
    "get_provider_models",
    
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