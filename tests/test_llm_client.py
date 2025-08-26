#!/usr/bin/env python3
"""
Test suite for LLM Client functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from maahelper.core.llm_client import (
    UnifiedLLMClient, 
    LLMConfig, 
    create_llm_client,
    get_all_providers,
    get_provider_models,
    LLMClientError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMModelError,
    LLMConnectionError
)


class TestLLMConfig:
    """Test LLM configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.api_key == "test-key"
        assert config.max_tokens == 2000
        assert config.temperature == 0.0
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            max_tokens=4000,
            temperature=0.5
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 4000
        assert config.temperature == 0.5


class TestUnifiedLLMClient:
    """Test Unified LLM Client"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client"""
        with patch('maahelper.core.llm_client.OpenAI') as mock_openai, \
             patch('maahelper.core.llm_client.AsyncOpenAI') as mock_async_openai:
            yield mock_openai, mock_async_openai
    
    def test_client_initialization(self, mock_openai_client):
        """Test client initialization"""
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        assert client.config == config
        assert client.provider_config is not None
    
    def test_chat_completion_success(self, mock_openai_client):
        """Test successful chat completion"""
        mock_openai, mock_async_openai = mock_openai_client
        
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat_completion(messages)
        
        assert response == "Test response"
        mock_client_instance.chat.completions.create.assert_called_once()
    
    def test_chat_completion_authentication_error(self, mock_openai_client):
        """Test authentication error handling"""
        mock_openai, mock_async_openai = mock_openai_client
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("Invalid API key")
        mock_openai.return_value = mock_client_instance
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="invalid-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMAuthenticationError):
            client.chat_completion(messages)
    
    def test_chat_completion_rate_limit_error(self, mock_openai_client):
        """Test rate limit error handling"""
        mock_openai, mock_async_openai = mock_openai_client
        
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        mock_openai.return_value = mock_client_instance
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMRateLimitError):
            client.chat_completion(messages)
    
    @pytest.mark.asyncio
    async def test_async_chat_completion(self, mock_openai_client):
        """Test async chat completion"""
        mock_openai, mock_async_openai = mock_openai_client
        
        # Mock async response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Async test response"
        
        mock_async_client_instance = Mock()
        mock_async_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_async_client_instance
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = await client.achat_completion(messages)
        
        assert response == "Async test response"
        mock_async_client_instance.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_chat_completion(self, mock_openai_client):
        """Test streaming chat completion"""
        mock_openai, mock_async_openai = mock_openai_client
        
        # Mock streaming response
        async def mock_stream():
            chunks = [
                Mock(choices=[Mock(delta=Mock(content="Hello"))]),
                Mock(choices=[Mock(delta=Mock(content=" world"))]),
                Mock(choices=[Mock(delta=Mock(content="!"))])
            ]
            for chunk in chunks:
                yield chunk
        
        mock_async_client_instance = Mock()
        mock_async_client_instance.chat.completions.create = AsyncMock(return_value=mock_stream())
        mock_async_openai.return_value = mock_async_client_instance
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        chunks = []
        async for chunk in client.stream_chat_completion(messages):
            chunks.append(chunk)
        
        assert chunks == ["Hello", " world", "!"]


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_all_providers(self):
        """Test getting all providers"""
        providers = get_all_providers()
        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "groq" in providers
    
    def test_get_provider_models(self):
        """Test getting provider models"""
        models = get_provider_models("openai")
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gpt-4o" in models
    
    def test_get_provider_models_invalid_provider(self):
        """Test getting models for invalid provider"""
        models = get_provider_models("invalid-provider")
        assert models == []
    
    def test_create_llm_client(self):
        """Test creating LLM client"""
        with patch('maahelper.core.llm_client.OpenAI'), \
             patch('maahelper.core.llm_client.AsyncOpenAI'):
            client = create_llm_client("openai", "gpt-4o", "test-key")
            assert isinstance(client, UnifiedLLMClient)
            assert client.config.provider == "openai"
            assert client.config.model == "gpt-4o"


class TestExceptionClasses:
    """Test custom exception classes"""
    
    def test_llm_client_error(self):
        """Test LLMClientError"""
        error = LLMClientError("Test error", provider="openai", model="gpt-4o")
        assert str(error) == "Test error"
        assert error.provider == "openai"
        assert error.model == "gpt-4o"
    
    def test_llm_authentication_error(self):
        """Test LLMAuthenticationError"""
        error = LLMAuthenticationError("Auth failed", provider="openai")
        assert str(error) == "Auth failed"
        assert error.provider == "openai"
    
    def test_llm_rate_limit_error(self):
        """Test LLMRateLimitError"""
        error = LLMRateLimitError("Rate limit", provider="openai")
        assert str(error) == "Rate limit"
        assert error.provider == "openai"
    
    def test_llm_model_error(self):
        """Test LLMModelError"""
        error = LLMModelError("Model error", model="invalid-model")
        assert str(error) == "Model error"
        assert error.model == "invalid-model"
    
    def test_llm_connection_error(self):
        """Test LLMConnectionError"""
        error = LLMConnectionError("Connection failed", provider="openai")
        assert str(error) == "Connection failed"
        assert error.provider == "openai"


if __name__ == "__main__":
    pytest.main([__file__])
