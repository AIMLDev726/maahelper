"""
AI Helper Agent - Modern Core Module
Core LLM client functionality for OpenAI-based system
"""

# Modern core components
from .llm_client import UnifiedLLMClient, create_llm_client, get_all_providers, get_provider_models

# Exports
__all__ = [
    "UnifiedLLMClient",
    "create_llm_client",
    "get_all_providers", 
    "get_provider_models"
]
