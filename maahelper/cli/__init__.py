"""
MaaHelper - Modern CLI Module
OpenAI-based CLI system with streamlined architecture
"""

from .modern_enhanced_cli import ModernEnhancedCLI, create_cli
from .modern_cli_selector import ModernCLISelector, cli_selector_entry

__all__ = [
    'ModernEnhancedCLI',
    'create_cli', 
    'ModernCLISelector',
    'cli_selector_entry'
]

# Version info
from .. import __version__
__author__ = "Meet Solanki (AIML Student)"
