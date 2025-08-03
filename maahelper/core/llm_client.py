"""
Unified LLM Client with OpenAI API support for multiple providers
Replaces LangChain with direct OpenAI client integration
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List, AsyncIterator, Union
from dataclasses import dataclass
from openai import OpenAI, AsyncOpenAI
from rich.console import Console

console = Console()

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.1
    stream: bool = True

class UnifiedLLMClient:
    """Unified client supporting multiple providers via OpenAI-compatible APIs"""
    
    # Provider configurations
    PROVIDER_CONFIGS = {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        },
        "google": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "models": ["llama2", "codellama", "mistral", "neural-chat"]
        }
    }
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider_config = self.PROVIDER_CONFIGS.get(config.provider, {})
        
        # Set base URL if not provided
        if not config.base_url and self.provider_config.get("base_url"):
            config.base_url = self.provider_config["base_url"]
        
        # Initialize clients
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        self.async_client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        console.print(f"✅ [green]LLM Client initialized: {config.provider.upper()} - {config.model}[/green]")
    
    @classmethod
    def create_from_provider(cls, provider: str, model: str, api_key: str, **kwargs) -> "UnifiedLLMClient":
        """Create client from provider name and model"""
        config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            **kwargs
        )
        return cls(config)
    
    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        return self.PROVIDER_CONFIGS.get(provider, {}).get("models", [])
    
    def detect_provider_from_model(self, model_name: str) -> Optional[str]:
        """Auto-detect provider from model name"""
        model_lower = model_name.lower()
        
        for provider, config in self.PROVIDER_CONFIGS.items():
            for model in config.get("models", []):
                if model.lower() in model_lower or any(part in model_lower for part in model.lower().split("-")):
                    return provider
        
        # Fallback patterns
        if any(name in model_lower for name in ['gpt', 'openai']):
            return "openai"
        elif any(name in model_lower for name in ['claude', 'anthropic']):
            return "anthropic"
        elif any(name in model_lower for name in ['gemini', 'google']):
            return "google"
        elif any(name in model_lower for name in ['llama', 'mixtral', 'gemma']):
            return "groq"
        elif any(name in model_lower for name in ['mistral', 'codellama', 'neural-chat']):
            return "ollama"
        
        return None
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Synchronous chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                stream=False  # Non-streaming version
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"❌ [red]Chat completion error: {e}[/red]")
            return f"Error: {str(e)}"
    
    async def achat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Asynchronous chat completion"""
        try:
            response = await self.async_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"❌ [red]Async chat completion error: {e}[/red]")
            return f"Error: {str(e)}"
    
    async def stream_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        """Streaming chat completion"""
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            console.print(f"❌ [red]Streaming error: {e}[/red]")
            yield f"Error: {str(e)}"
    
    def simple_query(self, query: str, system_prompt: Optional[str] = None) -> str:
        """Simple query interface"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": query})
        
        return self.chat_completion(messages)
    
    async def async_simple_query(self, query: str, system_prompt: Optional[str] = None) -> str:
        """Async simple query interface"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": query})
        
        return await self.achat_completion(messages)
    
    async def stream_simple_query(self, query: str, system_prompt: Optional[str] = None) -> AsyncIterator[str]:
        """Streaming simple query interface"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": query})
        
        async for chunk in self.stream_chat_completion(messages):
            yield chunk


def create_llm_client(provider: str, model: str, api_key: str) -> UnifiedLLMClient:
    """Factory function to create LLM client"""
    return UnifiedLLMClient.create_from_provider(provider, model, api_key)


# Provider-specific helper functions
def get_provider_models(provider: str) -> List[str]:
    """Get available models for a provider"""
    return UnifiedLLMClient.PROVIDER_CONFIGS.get(provider, {}).get("models", [])


def get_all_providers() -> List[str]:
    """Get list of all supported providers"""
    return list(UnifiedLLMClient.PROVIDER_CONFIGS.keys())


def validate_model_for_provider(provider: str, model: str) -> bool:
    """Validate if model is available for provider"""
    available_models = get_provider_models(provider)
    return model in available_models or any(model in m for m in available_models)
