"""
MaaHelper - Modern Core Module
Core LLM client functionality for OpenAI-based system
"""

# Modern core components
from .llm_client import (
    UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models, get_provider_models_dynamic,
    LLMClientError, LLMConnectionError, LLMAuthenticationError, LLMRateLimitError, LLMModelError, LLMStreamingError
)

# Exports
__all__ = [
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
    "LLMStreamingError"
]
