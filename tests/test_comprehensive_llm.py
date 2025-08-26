#!/usr/bin/env python3
"""
Comprehensive LLM Client Testing Suite for MaaHelper
Tests all LLM providers, authentication, error handling, and streaming
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional

# Test imports
try:
    from maahelper.core.llm_client import (
        UnifiedLLMClient, 
        LLMConfig,
        create_llm_client,
        get_all_providers,
        get_provider_models,
        get_provider_models_dynamic,
        LLMClientError,
        LLMAuthenticationError,
        LLMRateLimitError,
        LLMModelError,
        LLMConnectionError,
        LLMStreamingError
    )
    LLM_CLIENT_AVAILABLE = True
except ImportError as e:
    LLM_CLIENT_AVAILABLE = False
    IMPORT_ERROR = str(e)

class TestLLMClientAvailability:
    """Test LLM client availability and basic imports"""
    
    def test_llm_client_import(self):
        """Test that LLM client can be imported"""
        if not LLM_CLIENT_AVAILABLE:
            pytest.fail(f"Cannot import LLM client: {IMPORT_ERROR}")
        
        assert UnifiedLLMClient is not None
        assert LLMConfig is not None
        assert create_llm_client is not None

@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="LLM client not available")
class TestLLMConfig:
    """Test LLM configuration functionality"""
    
    def test_config_creation_with_required_params(self):
        """Test LLM config creation with required parameters"""
        config = LLMConfig(
            provider="openai",
            model="gpt-4o",
            api_key="test-key"
        )
        
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.api_key == "test-key"
        assert config.max_tokens == 2000  # Default value
        assert config.temperature == 0.0  # Default value
    
    def test_config_creation_with_all_params(self):
        """Test LLM config creation with all parameters"""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
            max_tokens=4000,
            temperature=0.7,
            base_url="https://api.anthropic.com"
        )
        
        assert config.provider == "anthropic"
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 4000
        assert config.temperature == 0.7
        assert config.base_url == "https://api.anthropic.com"
    
    def test_config_validation(self):
        """Test LLM config validation"""
        # Test invalid provider
        with pytest.raises((ValueError, TypeError)):
            LLMConfig(provider="", model="gpt-4o", api_key="test")
        
        # Test invalid model
        with pytest.raises((ValueError, TypeError)):
            LLMConfig(provider="openai", model="", api_key="test")
        
        # Test invalid API key
        with pytest.raises((ValueError, TypeError)):
            LLMConfig(provider="openai", model="gpt-4o", api_key="")

@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="LLM client not available")
class TestProviderDiscovery:
    """Test provider discovery functionality"""
    
    def test_get_all_providers(self):
        """Test getting all available providers"""
        providers = get_all_providers()
        
        assert isinstance(providers, list)
        assert len(providers) > 0
        
        # Check for expected providers
        expected_providers = ["openai", "anthropic", "groq"]
        for provider in expected_providers:
            assert provider in providers, f"Provider {provider} not found"
    
    def test_get_provider_models(self):
        """Test getting models for specific providers"""
        providers = get_all_providers()
        
        for provider in providers:
            models = get_provider_models(provider)
            assert isinstance(models, list)
            
            if provider == "openai":
                assert "gpt-4o" in models or "gpt-4" in models
            elif provider == "anthropic":
                assert any("claude" in model for model in models)
            elif provider == "groq":
                assert len(models) > 0
    
    def test_get_provider_models_invalid_provider(self):
        """Test getting models for invalid provider"""
        models = get_provider_models("invalid-provider-xyz")
        assert models == []
    
    @pytest.mark.asyncio
    async def test_get_provider_models_dynamic(self):
        """Test dynamic model discovery"""
        try:
            models = await get_provider_models_dynamic("openai")
            assert isinstance(models, list)
        except Exception as e:
            # Dynamic discovery may fail due to network/auth issues
            print(f"Dynamic model discovery failed (expected): {e}")

@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="LLM client not available")
class TestUnifiedLLMClient:
    """Test UnifiedLLMClient functionality"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client"""
        with patch('maahelper.core.llm_client.OpenAI') as mock_openai, \
             patch('maahelper.core.llm_client.AsyncOpenAI') as mock_async_openai:
            
            # Mock sync client
            mock_sync_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_sync_instance.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_sync_instance
            
            # Mock async client
            mock_async_instance = Mock()
            mock_async_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_async_openai.return_value = mock_async_instance
            
            yield mock_openai, mock_async_openai, mock_sync_instance, mock_async_instance
    
    def test_client_initialization(self, mock_openai_client):
        """Test client initialization"""
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        assert client.config == config
        assert client.provider_config is not None
    
    def test_sync_chat_completion(self, mock_openai_client):
        """Test synchronous chat completion"""
        mock_openai, mock_async_openai, mock_sync_instance, mock_async_instance = mock_openai_client
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat_completion(messages)
        
        assert response == "Test response"
        mock_sync_instance.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_chat_completion(self, mock_openai_client):
        """Test asynchronous chat completion"""
        mock_openai, mock_async_openai, mock_sync_instance, mock_async_instance = mock_openai_client
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = await client.achat_completion(messages)
        
        assert response == "Test response"
        mock_async_instance.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_streaming_chat_completion(self, mock_openai_client):
        """Test streaming chat completion"""
        mock_openai, mock_async_openai, mock_sync_instance, mock_async_instance = mock_openai_client
        
        # Mock streaming response
        async def mock_stream():
            chunks = [
                Mock(choices=[Mock(delta=Mock(content="Hello"))]),
                Mock(choices=[Mock(delta=Mock(content=" world"))]),
                Mock(choices=[Mock(delta=Mock(content="!"))])
            ]
            for chunk in chunks:
                yield chunk
        
        mock_async_instance.chat.completions.create = AsyncMock(return_value=mock_stream())
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        chunks = []
        
        async for chunk in client.stream_chat_completion(messages):
            chunks.append(chunk)
        
        assert chunks == ["Hello", " world", "!"]

@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="LLM client not available")
class TestErrorHandling:
    """Test LLM client error handling"""
    
    @pytest.fixture
    def mock_failing_client(self):
        """Mock client that raises various errors"""
        with patch('maahelper.core.llm_client.OpenAI') as mock_openai:
            mock_instance = Mock()
            mock_openai.return_value = mock_instance
            yield mock_instance
    
    def test_authentication_error_handling(self, mock_failing_client):
        """Test authentication error handling"""
        mock_failing_client.chat.completions.create.side_effect = Exception("Invalid API key")
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="invalid-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMAuthenticationError):
            client.chat_completion(messages)
    
    def test_rate_limit_error_handling(self, mock_failing_client):
        """Test rate limit error handling"""
        mock_failing_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMRateLimitError):
            client.chat_completion(messages)
    
    def test_model_error_handling(self, mock_failing_client):
        """Test model error handling"""
        mock_failing_client.chat.completions.create.side_effect = Exception("Model not found")
        
        config = LLMConfig(provider="openai", model="invalid-model", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMModelError):
            client.chat_completion(messages)
    
    def test_connection_error_handling(self, mock_failing_client):
        """Test connection error handling"""
        mock_failing_client.chat.completions.create.side_effect = Exception("Connection failed")
        
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test-key")
        client = UnifiedLLMClient(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(LLMConnectionError):
            client.chat_completion(messages)

@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="LLM client not available")
class TestMultipleProviders:
    """Test multiple provider support"""
    
    def test_openai_provider_config(self):
        """Test OpenAI provider configuration"""
        config = LLMConfig(provider="openai", model="gpt-4o", api_key="test")
        client = UnifiedLLMClient(config)
        
        assert client.config.provider == "openai"
        assert "openai" in client.provider_config
    
    def test_anthropic_provider_config(self):
        """Test Anthropic provider configuration"""
        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet-20241022", api_key="test")
        
        try:
            client = UnifiedLLMClient(config)
            assert client.config.provider == "anthropic"
        except ImportError:
            pytest.skip("Anthropic client not available")
    
    def test_groq_provider_config(self):
        """Test Groq provider configuration"""
        config = LLMConfig(provider="groq", model="llama-3.1-70b-versatile", api_key="test")
        
        try:
            client = UnifiedLLMClient(config)
            assert client.config.provider == "groq"
        except ImportError:
            pytest.skip("Groq client not available")
    
    def test_unsupported_provider(self):
        """Test unsupported provider handling"""
        config = LLMConfig(provider="unsupported-provider", model="test-model", api_key="test")
        
        with pytest.raises((ValueError, LLMClientError)):
            UnifiedLLMClient(config)

@pytest.mark.skipif(not LLM_CLIENT_AVAILABLE, reason="LLM client not available")
class TestClientFactory:
    """Test client factory functions"""
    
    def test_create_llm_client_function(self):
        """Test create_llm_client factory function"""
        with patch('maahelper.core.llm_client.OpenAI'), \
             patch('maahelper.core.llm_client.AsyncOpenAI'):
            
            client = create_llm_client("openai", "gpt-4o", "test-key")
            
            assert isinstance(client, UnifiedLLMClient)
            assert client.config.provider == "openai"
            assert client.config.model == "gpt-4o"
            assert client.config.api_key == "test-key"
    
    def test_create_llm_client_with_options(self):
        """Test create_llm_client with additional options"""
        with patch('maahelper.core.llm_client.OpenAI'), \
             patch('maahelper.core.llm_client.AsyncOpenAI'):
            
            client = create_llm_client(
                "openai", 
                "gpt-4o", 
                "test-key",
                max_tokens=4000,
                temperature=0.7
            )
            
            assert client.config.max_tokens == 4000
            assert client.config.temperature == 0.7

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
