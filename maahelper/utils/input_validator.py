#!/usr/bin/env python3
"""
Input Validation and Sanitization
Comprehensive input validation, sanitization, and security checks
"""

import re
import os
import html
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse

from rich.console import Console

console = Console()


@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    sanitized_value: Any
    errors: List[str]
    warnings: List[str]


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Security patterns
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # eval() calls
        r'exec\s*\(',  # exec() calls
        r'import\s+os',  # OS imports
        r'__import__',  # Dynamic imports
        r'\.\./',  # Path traversal
        r'\.\.\\',  # Path traversal (Windows)
    ]
    
    # File extension whitelist
    SAFE_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', 
        '.yaml', '.yml', '.xml', '.csv', '.log', '.ini', '.cfg', '.toml'
    }
    
    # Maximum lengths
    MAX_STRING_LENGTH = 10000
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_PATH_LENGTH = 260  # Windows limit
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]
    
    def validate_string(self, value: str, max_length: Optional[int] = None, allow_html: bool = False) -> ValidationResult:
        """Validate and sanitize string input"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            return ValidationResult(False, "", ["Input must be a string"], [])
        
        # Check length
        max_len = max_length or self.MAX_STRING_LENGTH
        if len(value) > max_len:
            errors.append(f"String too long (max {max_len} characters)")
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                errors.append(f"Potentially dangerous content detected: {pattern.pattern}")
        
        # Sanitize
        sanitized = value.strip()
        
        if not allow_html:
            # Escape HTML entities
            sanitized = html.escape(sanitized)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        # Check for suspicious Unicode
        if any(ord(char) > 0xFFFF for char in sanitized):
            warnings.append("Contains high Unicode characters")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized,
            errors=errors,
            warnings=warnings
        )
    
    def validate_file_path(self, path: str, must_exist: bool = False, must_be_file: bool = True) -> ValidationResult:
        """Validate file path for security and existence"""
        errors = []
        warnings = []
        
        if not isinstance(path, str):
            return ValidationResult(False, "", ["Path must be a string"], [])
        
        # Basic sanitization
        sanitized_path = path.strip()
        
        # Check length
        if len(sanitized_path) > self.MAX_PATH_LENGTH:
            errors.append(f"Path too long (max {self.MAX_PATH_LENGTH} characters)")
        
        # Check for path traversal
        if '..' in sanitized_path:
            errors.append("Path traversal detected")
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '|', '*', '?', '"']
        if any(char in sanitized_path for char in dangerous_chars):
            errors.append("Path contains dangerous characters")
        
        # Convert to Path object
        try:
            path_obj = Path(sanitized_path)
            
            # Check if path is absolute and outside allowed areas
            if path_obj.is_absolute():
                # Allow only certain absolute paths
                allowed_roots = [Path.home(), Path.cwd()]
                if not any(str(path_obj).startswith(str(root)) for root in allowed_roots):
                    warnings.append("Absolute path outside allowed directories")
            
            # Resolve path
            try:
                resolved_path = path_obj.resolve()
                sanitized_path = str(resolved_path)
            except (OSError, RuntimeError):
                errors.append("Invalid path")
            
            # Check existence if required
            if must_exist and not path_obj.exists():
                errors.append("Path does not exist")
            
            # Check if it's a file when required
            if must_be_file and path_obj.exists() and not path_obj.is_file():
                errors.append("Path is not a file")
            
            # Check file extension
            if path_obj.suffix.lower() not in self.SAFE_EXTENSIONS:
                warnings.append(f"Potentially unsafe file extension: {path_obj.suffix}")
            
        except Exception as e:
            errors.append(f"Path validation error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_path,
            errors=errors,
            warnings=warnings
        )
    
    def validate_url(self, url: str) -> ValidationResult:
        """Validate URL for security"""
        errors = []
        warnings = []
        
        if not isinstance(url, str):
            return ValidationResult(False, "", ["URL must be a string"], [])
        
        sanitized_url = url.strip()
        
        # Basic URL validation
        try:
            parsed = urlparse(sanitized_url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                errors.append("Only HTTP and HTTPS URLs are allowed")
            
            # Check for localhost/private IPs
            if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                warnings.append("URL points to localhost")
            
            # Check for private IP ranges
            if parsed.hostname and self._is_private_ip(parsed.hostname):
                warnings.append("URL points to private IP address")
            
            # Check for dangerous protocols
            if parsed.scheme in ['file', 'ftp', 'javascript', 'data']:
                errors.append(f"Dangerous URL scheme: {parsed.scheme}")
            
        except Exception as e:
            errors.append(f"Invalid URL format: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_url,
            errors=errors,
            warnings=warnings
        )
    
    def validate_api_key(self, api_key: str) -> ValidationResult:
        """Validate API key format and security"""
        errors = []
        warnings = []
        
        if not isinstance(api_key, str):
            return ValidationResult(False, "", ["API key must be a string"], [])
        
        sanitized_key = api_key.strip()
        
        # Check length
        if len(sanitized_key) < 10:
            errors.append("API key too short")
        
        if len(sanitized_key) > 200:
            errors.append("API key too long")
        
        # Check for suspicious patterns
        if sanitized_key.startswith('sk-') and len(sanitized_key) < 40:
            warnings.append("OpenAI API key appears to be incomplete")
        
        # Check for spaces (usually not allowed in API keys)
        if ' ' in sanitized_key:
            warnings.append("API key contains spaces")
        
        # Don't log the actual key for security
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_key,
            errors=errors,
            warnings=warnings
        )
    
    def validate_model_name(self, model: str) -> ValidationResult:
        """Validate model name"""
        errors = []
        warnings = []
        
        if not isinstance(model, str):
            return ValidationResult(False, "", ["Model name must be a string"], [])
        
        sanitized_model = model.strip().lower()
        
        # Check format
        if not re.match(r'^[a-z0-9\-\.]+$', sanitized_model):
            errors.append("Model name contains invalid characters")
        
        # Check length
        if len(sanitized_model) > 100:
            errors.append("Model name too long")
        
        if len(sanitized_model) < 2:
            errors.append("Model name too short")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_model,
            errors=errors,
            warnings=warnings
        )
    
    def validate_provider_name(self, provider: str) -> ValidationResult:
        """Validate provider name"""
        errors = []
        warnings = []
        
        if not isinstance(provider, str):
            return ValidationResult(False, "", ["Provider name must be a string"], [])
        
        sanitized_provider = provider.strip().lower()
        
        # Check format
        if not re.match(r'^[a-z0-9\-_]+$', sanitized_provider):
            errors.append("Provider name contains invalid characters")
        
        # Check against known providers
        known_providers = ['openai', 'anthropic', 'groq', 'google', 'cohere', 'huggingface']
        if sanitized_provider not in known_providers:
            warnings.append(f"Unknown provider: {sanitized_provider}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_provider,
            errors=errors,
            warnings=warnings
        )
    
    def validate_integer(self, value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> ValidationResult:
        """Validate integer input"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, str):
                sanitized_value = int(value.strip())
            else:
                sanitized_value = int(value)
        except (ValueError, TypeError):
            return ValidationResult(False, 0, ["Value must be an integer"], [])
        
        # Check range
        if min_val is not None and sanitized_value < min_val:
            errors.append(f"Value must be at least {min_val}")
        
        if max_val is not None and sanitized_value > max_val:
            errors.append(f"Value must be at most {max_val}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_value,
            errors=errors,
            warnings=warnings
        )
    
    def validate_float(self, value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> ValidationResult:
        """Validate float input"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, str):
                sanitized_value = float(value.strip())
            else:
                sanitized_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(False, 0.0, ["Value must be a number"], [])
        
        # Check for NaN and infinity
        if not (sanitized_value == sanitized_value):  # NaN check
            errors.append("Value cannot be NaN")
        
        if sanitized_value == float('inf') or sanitized_value == float('-inf'):
            errors.append("Value cannot be infinite")
        
        # Check range
        if min_val is not None and sanitized_value < min_val:
            errors.append(f"Value must be at least {min_val}")
        
        if max_val is not None and sanitized_value > max_val:
            errors.append(f"Value must be at most {max_val}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            sanitized_value=sanitized_value,
            errors=errors,
            warnings=warnings
        )
    
    def _is_private_ip(self, hostname: str) -> bool:
        """Check if hostname is a private IP address"""
        try:
            import ipaddress
            ip = ipaddress.ip_address(hostname)
            return ip.is_private
        except ValueError:
            return False


# Global validator instance
input_validator = InputValidator()
