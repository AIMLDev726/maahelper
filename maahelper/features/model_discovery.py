#!/usr/bin/env python3
"""
Dynamic Model Discovery System
Auto-fetch available models from provider APIs with caching and TTL
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiohttp
from rich.console import Console

console = Console()


@dataclass
class ModelInfo:
    """Information about a model"""
    id: str
    name: str
    provider: str
    context_length: int = 0
    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0
    supports_streaming: bool = True
    supports_function_calling: bool = False
    description: str = ""
    created: Optional[int] = None


@dataclass
class ModelCache:
    """Cache for model information"""
    models: Dict[str, List[ModelInfo]]
    last_updated: float
    ttl: int = 3600  # 1 hour default TTL


class DynamicModelDiscovery:
    """Dynamic model discovery with caching and auto-updates"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl: int = 3600):
        self.ttl = ttl
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".maahelper" / "cache"
        self.cache_file = self.cache_dir / "models.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Optional[ModelCache] = None
        
        # Provider configurations
        self.providers = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "models_endpoint": "/models",
                "requires_auth": True,
                "model_mapping": self._map_openai_models
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1",
                "models_endpoint": "/models",
                "requires_auth": True,
                "model_mapping": self._map_anthropic_models
            },
            "groq": {
                "base_url": "https://api.groq.com/openai/v1",
                "models_endpoint": "/models",
                "requires_auth": True,
                "model_mapping": self._map_groq_models
            },
            "google": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "models_endpoint": "/models",
                "requires_auth": True,
                "model_mapping": self._map_google_models
            }
        }
    
    async def get_available_models(self, provider: Optional[str] = None, force_refresh: bool = False) -> Dict[str, List[ModelInfo]]:
        """Get available models for all providers or a specific provider"""
        if not force_refresh and self._is_cache_valid():
            return self._load_cache().models
        
        console.print("🔍 [cyan]Discovering available models...[/cyan]")
        
        all_models = {}
        providers_to_check = [provider] if provider else list(self.providers.keys())
        
        for provider_name in providers_to_check:
            try:
                models = await self._fetch_provider_models(provider_name)
                if models:
                    # Apply additional chat completion filtering
                    chat_models = self._filter_chat_completion_models(models)
                    all_models[provider_name] = chat_models
                    console.print(f"✅ [green]Found {len(chat_models)} chat models for {provider_name}[/green]")
                    if len(models) > len(chat_models):
                        filtered_count = len(models) - len(chat_models)
                        console.print(f"   [dim]Filtered out {filtered_count} non-chat models (TTS, embeddings, etc.)[/dim]")
                else:
                    console.print(f"⚠️ [yellow]No models found for {provider_name}[/yellow]")
            except Exception as e:
                console.print(f"❌ [red]Error fetching models for {provider_name}: {e}[/red]")
                # Use fallback models if available
                fallback_models = self._get_fallback_models(provider_name)
                if fallback_models:
                    # Also filter fallback models
                    chat_fallback = self._filter_chat_completion_models(fallback_models)
                    all_models[provider_name] = chat_fallback
        
        # Cache the results
        self._save_cache(all_models)
        
        return all_models
    
    async def _fetch_provider_models(self, provider: str) -> List[ModelInfo]:
        """Fetch models from a specific provider"""
        if provider not in self.providers:
            return []
        
        config = self.providers[provider]
        
        # Get API key from environment
        import os
        api_key_env = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_env)
        
        if config["requires_auth"] and not api_key:
            console.print(f"⚠️ [yellow]No API key found for {provider} (set {api_key_env})[/yellow]")
            return self._get_fallback_models(provider)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if api_key:
                    if provider == "anthropic":
                        headers["x-api-key"] = api_key
                        headers["anthropic-version"] = "2023-06-01"
                    else:
                        headers["Authorization"] = f"Bearer {api_key}"

                url = config["base_url"] + config["models_endpoint"]
                
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return config["model_mapping"](data)
                    else:
                        console.print(f"⚠️ [yellow]API request failed for {provider}: {response.status}[/yellow]")
                        return self._get_fallback_models(provider)
        
        except Exception as e:
            console.print(f"⚠️ [yellow]Network error for {provider}: {e}[/yellow]")
            return self._get_fallback_models(provider)
    
    def _map_openai_models(self, data: Dict[str, Any]) -> List[ModelInfo]:
        """Map OpenAI API response to ModelInfo objects (chat completion models only)"""
        models = []

        # Define chat completion model patterns (exclude TTS, embeddings, image models)
        chat_patterns = ["gpt-4", "gpt-3.5-turbo", "gpt-3.5", "text-davinci", "text-curie"]
        exclude_patterns = [
            "whisper",      # TTS models
            "tts-",         # Text-to-speech
            "dall-e",       # Image generation
            "embedding",    # Embedding models
            "text-embedding", # Embedding models
            "moderation",   # Moderation models
            "babbage",      # Legacy completion models
            "ada",          # Legacy completion models
            "curie-instruct", # Legacy instruct models
            "davinci-instruct" # Legacy instruct models
        ]

        for model_data in data.get("data", []):
            model_id = model_data.get("id", "").lower()

            # Check if it's a chat completion model
            is_chat_model = any(pattern in model_id for pattern in chat_patterns)
            is_excluded = any(pattern in model_id for pattern in exclude_patterns)

            if is_chat_model and not is_excluded:
                models.append(ModelInfo(
                    id=model_data.get("id", ""),  # Use original case
                    name=model_data.get("id", ""),
                    provider="openai",
                    context_length=self._get_openai_context_length(model_data.get("id", "")),
                    supports_streaming=True,
                    supports_function_calling="gpt-" in model_data.get("id", ""),
                    created=model_data.get("created")
                ))
        return models
    
    def _map_anthropic_models(self, data: Dict[str, Any]) -> List[ModelInfo]:
        """Map Anthropic API response to ModelInfo objects"""
        models = []

        # Try to parse actual API response first
        if "data" in data:
            for model_data in data["data"]:
                model_id = model_data.get("id", "")
                if "claude" in model_id.lower():
                    models.append(ModelInfo(
                        id=model_id,
                        name=model_data.get("display_name", model_id),
                        provider="anthropic",
                        context_length=self._get_anthropic_context_length(model_id),
                        supports_streaming=True,
                        supports_function_calling=True,
                        description=model_data.get("description", ""),
                        created=model_data.get("created_at")
                    ))

        # Fallback to known models if API response is empty or malformed
        if not models:
            known_models = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
            for model_id in known_models:
                models.append(ModelInfo(
                    id=model_id,
                    name=model_id,
                    provider="anthropic",
                    context_length=self._get_anthropic_context_length(model_id),
                    supports_streaming=True,
                    supports_function_calling=True
                ))

        return models
    
    def _map_groq_models(self, data: Dict[str, Any]) -> List[ModelInfo]:
        """Map Groq API response to ModelInfo objects (chat completion models only)"""
        models = []

        # Define chat completion model patterns for Groq
        chat_patterns = [
            "llama",
            "mixtral",
            "gemma",
            "mistral",
            "qwen",
            "deepseek"
        ]

        # Exclude non-chat models
        exclude_patterns = [
            "whisper",      # Speech-to-text
            "embedding",    # Embedding models
            "tts",          # Text-to-speech
            "vision",       # Vision models (if not chat)
            "tool-use"      # Tool-specific models
        ]

        for model_data in data.get("data", []):
            model_id = model_data.get("id", "").lower()

            # Check if it's a chat completion model
            is_chat_model = any(pattern in model_id for pattern in chat_patterns)
            is_excluded = any(pattern in model_id for pattern in exclude_patterns)

            if is_chat_model and not is_excluded:
                models.append(ModelInfo(
                    id=model_data.get("id", ""),  # Use original case
                    name=model_data.get("id", ""),
                    provider="groq",
                    context_length=32768,  # Most Groq models support 32k context
                    supports_streaming=True,
                    supports_function_calling=False,
                    created=model_data.get("created")
                ))
        return models
    
    def _map_google_models(self, data: Dict[str, Any]) -> List[ModelInfo]:
        """Map Google API response to ModelInfo objects (chat completion models only)"""
        models = []

        # Define chat completion model patterns for Google
        chat_patterns = ["gemini"]

        # Exclude non-chat models
        exclude_patterns = [
            "embedding",    # Embedding models
            "vision",       # Vision-only models (if not chat)
            "tts",          # Text-to-speech
            "translate",    # Translation models
            "summarize"     # Summarization-only models
        ]

        for model_data in data.get("models", []):
            model_name = model_data.get("name", "").lower()

            # Check if it's a chat completion model
            is_chat_model = any(pattern in model_name for pattern in chat_patterns)
            is_excluded = any(pattern in model_name for pattern in exclude_patterns)

            # Additional check: ensure it supports generateContent (chat capability)
            supported_methods = model_data.get("supportedGenerationMethods", [])
            supports_chat = "generateContent" in supported_methods if supported_methods else True

            if is_chat_model and not is_excluded and supports_chat:
                original_name = model_data.get("name", "")
                model_id = original_name.split("/")[-1] if "/" in original_name else original_name

                models.append(ModelInfo(
                    id=model_id,
                    name=model_id,
                    provider="google",
                    context_length=1000000 if "1.5" in model_id else 32768,
                    supports_streaming=True,
                    supports_function_calling=True
                ))
        return models

    def _filter_chat_completion_models(self, models: List[ModelInfo]) -> List[ModelInfo]:
        """Additional filtering to ensure only chat completion models"""
        chat_models = []

        # Common non-chat model patterns across all providers
        non_chat_patterns = [
            "whisper",          # Speech-to-text
            "tts-",             # Text-to-speech
            "dall-e",           # Image generation
            "embedding",        # Embedding models
            "text-embedding",   # Embedding models
            "moderation",       # Content moderation
            "vision-only",      # Vision-only models
            "translate",        # Translation models
            "summarize-only",   # Summarization-only
            "code-search",      # Code search models
            "rerank",           # Reranking models
        ]

        for model in models:
            model_id_lower = model.id.lower()
            is_non_chat = any(pattern in model_id_lower for pattern in non_chat_patterns)

            if not is_non_chat:
                chat_models.append(model)

        return chat_models

    def _get_openai_context_length(self, model_id: str) -> int:
        """Get context length for OpenAI models"""
        context_lengths = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385,
        }
        
        for model_prefix, length in context_lengths.items():
            if model_id.startswith(model_prefix):
                return length
        
        return 4096  # Default

    def _get_anthropic_context_length(self, model_id: str) -> int:
        """Get context length for Anthropic models"""
        context_lengths = {
            "claude-3-5-sonnet": 200000,
            "claude-3-5-haiku": 200000,
            "claude-3-opus": 200000,
            "claude-3-sonnet": 200000,
            "claude-3-haiku": 200000,
            "claude-2": 100000,
        }

        for model_prefix, length in context_lengths.items():
            if model_id.startswith(model_prefix):
                return length

        return 100000  # Default for Claude models
    
    def _get_fallback_models(self, provider: str) -> List[ModelInfo]:
        """Get fallback models when API is unavailable"""
        fallback_models = {
            "openai": [
                ModelInfo("gpt-4o", "GPT-4o", "openai", 128000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("gpt-4o-mini", "GPT-4o Mini", "openai", 128000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("gpt-4-turbo", "GPT-4 Turbo", "openai", 128000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("gpt-3.5-turbo", "GPT-3.5 Turbo", "openai", 16385, supports_streaming=True, supports_function_calling=True),
            ],
            "anthropic": [
                ModelInfo("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet", "anthropic", 200000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("claude-3-5-haiku-20241022", "Claude 3.5 Haiku", "anthropic", 200000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("claude-3-opus-20240229", "Claude 3 Opus", "anthropic", 200000, supports_streaming=True, supports_function_calling=True),
            ],
            "groq": [
                ModelInfo("llama-3.1-70b-versatile", "Llama 3.1 70B", "groq", 32768, supports_streaming=True),
                ModelInfo("llama-3.1-8b-instant", "Llama 3.1 8B", "groq", 32768, supports_streaming=True),
                ModelInfo("mixtral-8x7b-32768", "Mixtral 8x7B", "groq", 32768, supports_streaming=True),
            ],
            "google": [
                ModelInfo("gemini-1.5-pro", "Gemini 1.5 Pro", "google", 1000000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("gemini-1.5-flash", "Gemini 1.5 Flash", "google", 1000000, supports_streaming=True, supports_function_calling=True),
                ModelInfo("gemini-pro", "Gemini Pro", "google", 32768, supports_streaming=True, supports_function_calling=True),
            ]
        }
        
        return fallback_models.get(provider, [])
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is valid and not expired"""
        if not self.cache_file.exists():
            return False
        
        cache = self._load_cache()
        if not cache:
            return False
        
        return (time.time() - cache.last_updated) < self.ttl
    
    def _load_cache(self) -> Optional[ModelCache]:
        """Load cache from disk"""
        if self._cache:
            return self._cache
        
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert dict back to ModelInfo objects
                models = {}
                for provider, model_list in data.get("models", {}).items():
                    models[provider] = [ModelInfo(**model_data) for model_data in model_list]
                
                self._cache = ModelCache(
                    models=models,
                    last_updated=data.get("last_updated", 0),
                    ttl=data.get("ttl", self.ttl)
                )
                return self._cache
        except Exception as e:
            console.print(f"⚠️ [yellow]Error loading model cache: {e}[/yellow]")
        
        return None
    
    def _save_cache(self, models: Dict[str, List[ModelInfo]]) -> None:
        """Save cache to disk"""
        try:
            # Convert ModelInfo objects to dicts
            models_dict = {}
            for provider, model_list in models.items():
                models_dict[provider] = [asdict(model) for model in model_list]
            
            cache_data = {
                "models": models_dict,
                "last_updated": time.time(),
                "ttl": self.ttl
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            
            # Update in-memory cache
            self._cache = ModelCache(
                models=models,
                last_updated=cache_data["last_updated"],
                ttl=self.ttl
            )
            
        except Exception as e:
            console.print(f"⚠️ [yellow]Error saving model cache: {e}[/yellow]")
    
    def get_model_info(self, provider: str, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        if self._cache and provider in self._cache.models:
            for model in self._cache.models[provider]:
                if model.id == model_id:
                    return model
        return None
    
    def list_models_by_capability(self, capability: str) -> List[ModelInfo]:
        """List models that support a specific capability"""
        if not self._cache:
            return []
        
        matching_models = []
        for provider_models in self._cache.models.values():
            for model in provider_models:
                if capability == "streaming" and model.supports_streaming:
                    matching_models.append(model)
                elif capability == "function_calling" and model.supports_function_calling:
                    matching_models.append(model)
                elif capability == "long_context" and model.context_length > 32768:
                    matching_models.append(model)
        
        return matching_models


# Global instance
model_discovery = DynamicModelDiscovery()
