"""
Unified LLM Client with OpenAI API support for multiple providers
Replaces LangChain with direct OpenAI client integration
"""

from typing import Dict, Optional, List, AsyncIterator
from dataclasses import dataclass
from openai import OpenAI, AsyncOpenAI
from rich.console import Console
from rich.prompt import Prompt

console = Console()


# Custom Exception Classes
class LLMClientError(Exception):
    """Base exception for LLM client errors"""
    def __init__(self, message: str, provider: str = None, model: str = None, original_error: Exception = None):
        self.message = message
        self.provider = provider
        self.model = model
        self.original_error = original_error
        super().__init__(self.message)


class LLMConnectionError(LLMClientError):
    """Exception for connection-related errors"""
    pass


class LLMAuthenticationError(LLMClientError):
    """Exception for authentication-related errors"""
    pass


class LLMRateLimitError(LLMClientError):
    """Exception for rate limit errors"""
    pass


class LLMModelError(LLMClientError):
    """Exception for model-related errors"""
    pass


class LLMStreamingError(LLMClientError):
    """Exception for streaming-related errors"""
    pass

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.0
    stream: bool = True

class UnifiedLLMClient:
    """Unified client supporting multiple providers via OpenAI-compatible APIs"""
    
    # Provider configurations
    PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0125"
        ]
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b",
            "gemma2-9b-it",
            "mistral-7b-instruct-v0.2",
            "llama-3-70b-instruct",
            "llama-3-8b-instruct"
        ]
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "models": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "models": []
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "models": []
    },
    "fireworks": {
        "base_url": "https://api.fireworks.ai/inference/v1",
        "models": []
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "models": []
    },
    "localai": {
        "base_url": "http://localhost:8080/v1",
        "models": []
    },
    "deepinfra": {
        "base_url": "https://api.deepinfra.com/v1/openai",
        "models": []
    },
    "perplexity": {
        "base_url": "https://api.perplexity.ai/chat/completions",
        "models": []
    },
    "cerebras": {
        "base_url": "https://api.cerebras.net/v1",
        "models": []
    }
}

    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider_config = self.PROVIDER_CONFIGS.get(config.provider, {})
        
        # Set base URL if not provided
        if not config.base_url and self.provider_config.get("base_url"):
            config.base_url = self.provider_config.get("base_url")
        
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

    async def fetch_models_from_api(self, provider: str, api_key: str) -> List[str]:
        """Fetch available models dynamically from provider API"""
        try:
            import aiohttp

            config = self.PROVIDER_CONFIGS.get(provider, {})
            base_url = config.get("base_url", "")

            if not base_url:
                return []

            # Construct models endpoint URL
            if provider == "openai":
                models_url = f"{base_url}/models"
                headers = {"Authorization": f"Bearer {api_key}"}
            elif provider == "groq":
                models_url = f"{base_url}/models"
                headers = {"Authorization": f"Bearer {api_key}"}
            elif provider == "anthropic":
                # Anthropic doesn't have a public models endpoint, return static list
                return self.get_available_models(provider)
            elif provider == "google":
                # Google Gemini models endpoint
                models_url = f"{base_url}/models?key={api_key}"
                headers = {}
            else:
                # For other providers, try OpenAI-compatible endpoint
                models_url = f"{base_url}/models"
                headers = {"Authorization": f"Bearer {api_key}"}

            async with aiohttp.ClientSession() as session:
                async with session.get(models_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Parse response based on provider
                        if provider in ["openai", "groq"] or "openai" in base_url:
                            # OpenAI-compatible format
                            models = [model["id"] for model in data.get("data", [])]
                        elif provider == "google":
                            # Google format
                            models = [model["name"].split("/")[-1] for model in data.get("models", [])]
                        else:
                            # Try to extract model names from various formats
                            if "data" in data:
                                models = [model.get("id", model.get("name", "")) for model in data["data"]]
                            elif "models" in data:
                                models = [model.get("id", model.get("name", "")) for model in data["models"]]
                            else:
                                models = []

                        # Filter out empty names and return
                        return [model for model in models if model]
                    else:
                        print(f"Failed to fetch models for {provider}: HTTP {response.status}")
                        return self.get_available_models(provider)

        except ImportError:
            print("aiohttp not available, falling back to static models")
            return self.get_available_models(provider)
        except Exception as e:
            print(f"Error fetching models for {provider}: {e}")
            return self.get_available_models(provider)
    
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
    
    def get_provider_models(provider: str) -> List[str]:
        """Get available models for a provider"""

        # Providers that must ask user for model names manually
        always_prompt = [
            "ollama", "together", "fireworks", "openrouter",
            "localai", "deepinfra", "perplexity", "cerebras"
        ]

        if provider in always_prompt:
            console.print(f"[yellow]⚠ Models not predefined for '{provider}'.[/yellow]")
            model_input = Prompt.ask(f"🔧 Enter one or more model names for '{provider}' (comma-separated)")
            models = [m.strip() for m in model_input.split(",") if m.strip()]
            return models

        # Fallback to predefined config
        return UnifiedLLMClient.PROVIDER_CONFIGS.get(provider, {}).get("models", [])

    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Synchronous chat completion"""
        try:
            # Prepare request parameters
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": False  # Non-streaming version
            }

            # Explicitly disable tool calling to prevent "Tool choice is none" error
            request_params["tools"] = None
            request_params["tool_choice"] = None

            # Remove None values to avoid API issues
            request_params = {k: v for k, v in request_params.items() if v is not None}

            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content

        except Exception as e:
            console.print(f"❌ [red]Chat completion error: {e}[/red]")
            # Enhanced error handling for tool-related issues
            error_msg = str(e).lower()

            # Handle tool calling specific errors
            if "tool choice" in error_msg or "function" in error_msg:
                console.print(f"[yellow]⚠️ Tool calling issue detected. Retrying without tools...[/yellow]")
                try:
                    # Retry without any tool-related parameters
                    retry_params = {
                        "model": self.config.model,
                        "messages": messages,
                        "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                        "temperature": kwargs.get('temperature', self.config.temperature),
                        "stream": False
                    }

                    response = self.client.chat.completions.create(**retry_params)
                    return response.choices[0].message.content
                except Exception as retry_error:
                    console.print(f"[red]Retry also failed: {retry_error}[/red]")
                    e = retry_error  # Use the retry error for further processing
                    error_msg = str(e).lower()

            # Classify the error and raise appropriate exception
            if "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg:
                raise LLMAuthenticationError(
                    f"Authentication failed for {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "rate limit" in error_msg or "quota" in error_msg:
                raise LLMRateLimitError(
                    f"Rate limit exceeded for {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "model" in error_msg or "not found" in error_msg:
                raise LLMModelError(
                    f"Model error for {self.config.model} on {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                raise LLMConnectionError(
                    f"Connection error to {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            else:
                raise LLMClientError(
                    f"Chat completion failed: {str(e)}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
    
    async def achat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Asynchronous chat completion"""
        try:
            # Prepare request parameters
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": False
            }

            # Explicitly disable tool calling to prevent "Tool choice is none" error
            request_params["tools"] = None
            request_params["tool_choice"] = None

            # Remove None values to avoid API issues
            request_params = {k: v for k, v in request_params.items() if v is not None}

            response = await self.async_client.chat.completions.create(**request_params)
            return response.choices[0].message.content

        except Exception as e:
            console.print(f"❌ [red]Async chat completion error: {e}[/red]")
            # Enhanced error handling for tool-related issues
            error_msg = str(e).lower()

            # Handle tool calling specific errors
            if "tool choice" in error_msg or "function" in error_msg:
                console.print(f"[yellow]⚠️ Tool calling issue detected. Retrying without tools...[/yellow]")
                try:
                    # Retry without any tool-related parameters
                    retry_params = {
                        "model": self.config.model,
                        "messages": messages,
                        "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                        "temperature": kwargs.get('temperature', self.config.temperature),
                        "stream": False
                    }

                    response = await self.async_client.chat.completions.create(**retry_params)
                    return response.choices[0].message.content
                except Exception as retry_error:
                    console.print(f"[red]Retry also failed: {retry_error}[/red]")
                    e = retry_error  # Use the retry error for further processing
                    error_msg = str(e).lower()

            # Classify the error and raise appropriate exception
            if "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg:
                raise LLMAuthenticationError(
                    f"Authentication failed for {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "rate limit" in error_msg or "quota" in error_msg:
                raise LLMRateLimitError(
                    f"Rate limit exceeded for {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "model" in error_msg or "not found" in error_msg:
                raise LLMModelError(
                    f"Model error for {self.config.model} on {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                raise LLMConnectionError(
                    f"Connection error to {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            else:
                raise LLMClientError(
                    f"Async chat completion failed: {str(e)}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
    
    async def stream_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        """Streaming chat completion"""
        try:
            # Prepare request parameters
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                "temperature": kwargs.get('temperature', self.config.temperature),
                "stream": True
            }

            # Explicitly disable tool calling to prevent "Tool choice is none" error
            # This ensures compatibility with models that don't support function calling
            request_params["tools"] = None
            request_params["tool_choice"] = None

            # Remove None values to avoid API issues
            request_params = {k: v for k, v in request_params.items() if v is not None}

            stream = await self.async_client.chat.completions.create(**request_params)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            console.print(f"❌ [red]Streaming error: {e}[/red]")
            # Enhanced error handling for tool-related issues
            error_msg = str(e).lower()

            # Handle tool calling specific errors
            if "tool choice" in error_msg or "function" in error_msg:
                console.print(f"[yellow]⚠️ Tool calling issue detected. Retrying without tools...[/yellow]")
                try:
                    # Retry without any tool-related parameters
                    retry_params = {
                        "model": self.config.model,
                        "messages": messages,
                        "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
                        "temperature": kwargs.get('temperature', self.config.temperature),
                        "stream": True
                    }

                    stream = await self.async_client.chat.completions.create(**retry_params)
                    async for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                    return
                except Exception as retry_error:
                    console.print(f"[red]Retry also failed: {retry_error}[/red]")
                    e = retry_error  # Use the retry error for further processing
                    error_msg = str(e).lower()

            # Classify the error and raise appropriate exception
            if "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg:
                raise LLMAuthenticationError(
                    f"Authentication failed for {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "rate limit" in error_msg or "quota" in error_msg:
                raise LLMRateLimitError(
                    f"Rate limit exceeded for {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "model" in error_msg or "not found" in error_msg:
                raise LLMModelError(
                    f"Model error for {self.config.model} on {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            elif "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                raise LLMConnectionError(
                    f"Connection error to {self.config.provider}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
            else:
                raise LLMStreamingError(
                    f"Streaming failed: {str(e)}",
                    provider=self.config.provider,
                    model=self.config.model,
                    original_error=e
                )
    
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

    async def stream_completion(self, query: str, system_prompt: Optional[str] = None) -> AsyncIterator[str]:
        """Stream completion method for compatibility with streaming handler"""
        # This method is called by the ModernStreamingHandler
        async for chunk in self.stream_simple_query(query, system_prompt):
            yield chunk


def create_llm_client(provider: str, model: str, api_key: str) -> UnifiedLLMClient:
    """Factory function to create LLM client"""
    return UnifiedLLMClient.create_from_provider(provider, model, api_key)


# Provider-specific helper functions
def get_provider_models(provider: str) -> List[str]:
    """Get available models for a provider (static fallback)"""
    return UnifiedLLMClient.PROVIDER_CONFIGS.get(provider, {}).get("models", [])


async def get_provider_models_dynamic(provider: str, api_key: Optional[str] = None) -> List[str]:
    """Get available models for a provider with dynamic fetching"""
    if api_key:
        try:
            # Create a temporary client instance to fetch models
            temp_client = UnifiedLLMClient(LLMConfig(
                provider=provider,
                model="temp",  # Temporary model name
                api_key=api_key
            ))
            dynamic_models = await temp_client.fetch_models_from_api(provider, api_key)
            if dynamic_models:
                return dynamic_models
        except Exception as e:
            print(f"Dynamic model fetching failed for {provider}: {e}")

    # Fallback to static models
    return get_provider_models(provider)


def get_all_providers() -> List[str]:
    """Get list of all supported providers"""
    return list(UnifiedLLMClient.PROVIDER_CONFIGS.keys())


def validate_model_for_provider(provider: str, model: str) -> bool:
    """Validate if model is available for provider"""
    available_models = get_provider_models(provider)
    return model in available_models or any(model in m for m in available_models)
