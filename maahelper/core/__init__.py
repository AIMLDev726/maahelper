"""
<<<<<<< HEAD
AI Helper Agent - Modern Core Module
=======
MaaHelper - Modern Core Module
>>>>>>> 9a27ace (Initial commit)
Core LLM client functionality for OpenAI-based system
"""

# Modern core components
<<<<<<< HEAD
from .llm_client import UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models
=======
from .llm_client import (
    UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models, get_provider_models_dynamic,
    LLMClientError, LLMConnectionError, LLMAuthenticationError, LLMRateLimitError, LLMModelError, LLMStreamingError
)
>>>>>>> 9a27ace (Initial commit)

# Exports
__all__ = [
    "UnifiedLLMClient",
    "create_llm_client",
<<<<<<< HEAD
    "get_all_providers", 
    "get_provider_models"
=======
    "get_all_providers",
    "get_provider_models",
    "get_provider_models_dynamic",
    # Exception classes
    "LLMClientError",
    "LLMConnectionError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelError",
    "LLMStreamingError"
>>>>>>> 9a27ace (Initial commit)
]
