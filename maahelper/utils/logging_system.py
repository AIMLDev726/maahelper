#!/usr/bin/env python3
"""
Structured Logging System
Configurable logging with structured output, file rotation, and performance monitoring
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

from rich.console import Console
from rich.logging import RichHandler

console = Console()


@dataclass
class LogConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "structured"  # "structured", "json", "simple"
    file_enabled: bool = True
    console_enabled: bool = True
    file_path: str = ""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    include_caller: bool = True
    include_timestamp: bool = True


class StructuredLogger:
    """Structured logging system with rich console output and file rotation"""
    
    def __init__(self, name: str = "maahelper", config: Optional[LogConfig] = None):
        self.name = name
        self.config = config or LogConfig()
        self.logger = None
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        if STRUCTLOG_AVAILABLE and self.config.format == "structured":
            self._setup_structlog()
        else:
            self._setup_standard_logging()
    
    def _setup_structlog(self) -> None:
        """Setup structured logging with structlog"""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if self.config.format == "json" else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Get logger
        self.logger = structlog.get_logger(self.name)
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_standard_logging(self) -> None:
        """Setup standard Python logging"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup logging handlers"""
        # Console handler with Rich
        if self.config.console_enabled:
            console_handler = RichHandler(
                console=console,
                show_time=self.config.include_timestamp,
                show_path=self.config.include_caller,
                rich_tracebacks=True
            )
            console_handler.setLevel(getattr(logging, self.config.level.upper()))
            
            if STRUCTLOG_AVAILABLE:
                # For structlog, add to root logger
                logging.getLogger().addHandler(console_handler)
            else:
                self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.file_enabled and self.config.file_path:
            file_path = Path(self.config.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, self.config.level.upper()))
            
            # File formatter
            if self.config.format == "json":
                file_formatter = JsonFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            file_handler.setFormatter(file_formatter)
            
            if STRUCTLOG_AVAILABLE:
                logging.getLogger().addHandler(file_handler)
            else:
                self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        if STRUCTLOG_AVAILABLE:
            self.logger.debug(message, **kwargs)
        else:
            self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(message, **kwargs)
        else:
            self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        if STRUCTLOG_AVAILABLE:
            self.logger.warning(message, **kwargs)
        else:
            self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        if STRUCTLOG_AVAILABLE:
            self.logger.error(message, **kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        if STRUCTLOG_AVAILABLE:
            self.logger.critical(message, **kwargs)
        else:
            self.logger.critical(message, extra=kwargs)
    
    def log_request(self, provider: str, model: str, tokens: int, duration: float, **kwargs) -> None:
        """Log API request with performance metrics"""
        self.info(
            "API Request",
            provider=provider,
            model=model,
            tokens=tokens,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log error with additional context"""
        self.error(
            f"Error: {str(error)}",
            error_type=type(error).__name__,
            context=context,
            exc_info=True
        )
    
    def log_performance(self, operation: str, duration: float, **metrics) -> None:
        """Log performance metrics"""
        self.info(
            f"Performance: {operation}",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            **metrics
        )


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'lineno', 'funcName', 'created', 
                              'msecs', 'relativeCreated', 'thread', 'threadName', 
                              'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                    log_data[key] = value
        
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class LoggerManager:
    """Manager for multiple loggers with different configurations"""
    
    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}
        self.default_config = LogConfig()
    
    def get_logger(self, name: str, config: Optional[LogConfig] = None) -> StructuredLogger:
        """Get or create a logger with the given name"""
        if name not in self.loggers:
            self.loggers[name] = StructuredLogger(name, config or self.default_config)
        return self.loggers[name]
    
    def configure_default(self, config: LogConfig) -> None:
        """Configure default logging settings"""
        self.default_config = config
    
    def set_level(self, level: str) -> None:
        """Set logging level for all loggers"""
        for logger in self.loggers.values():
            logger.config.level = level.upper()
            logger._setup_logging()
    
    def enable_file_logging(self, file_path: str) -> None:
        """Enable file logging for all loggers"""
        for logger in self.loggers.values():
            logger.config.file_enabled = True
            logger.config.file_path = file_path
            logger._setup_logging()
    
    def disable_console_logging(self) -> None:
        """Disable console logging for all loggers"""
        for logger in self.loggers.values():
            logger.config.console_enabled = False
            logger._setup_logging()


# Global logger manager
logger_manager = LoggerManager()

# Default application logger
app_logger = logger_manager.get_logger("maahelper")


def get_logger(name: str = "maahelper") -> StructuredLogger:
    """Get a logger instance"""
    return logger_manager.get_logger(name)


def configure_logging(
    level: str = "INFO",
    file_path: Optional[str] = None,
    format: str = "structured",
    console_enabled: bool = True
) -> None:
    """Configure global logging settings"""
    config = LogConfig(
        level=level,
        format=format,
        file_enabled=bool(file_path),
        file_path=file_path or "",
        console_enabled=console_enabled
    )
    logger_manager.configure_default(config)
    
    # Reconfigure existing loggers
    for logger in logger_manager.loggers.values():
        logger.config = config
        logger._setup_logging()
