"""
<<<<<<< HEAD
Streamlined API Key Manager for AI Helper Agent v0.0.4
=======
Streamlined API Key Manager for MaaHelper
>>>>>>> 9a27ace (Initial commit)
Uses the advanced secure local storage system
"""

from .advanced_api_key_manager import advanced_api_key_manager

# Export the advanced manager as the main API key manager
api_key_manager = advanced_api_key_manager

# Legacy compatibility
class StreamlinedAPIKeyManager:
    """Legacy compatibility wrapper"""
    
    def __init__(self):
        self.manager = advanced_api_key_manager
    
    def get_api_key(self, provider: str):
        return self.manager.get_api_key(provider)
    
    def get_available_providers(self):
        return self.manager.get_available_providers()
    
    def show_setup_guidance(self):
        return self.manager.show_provider_info()
    
    def show_provider_info(self):
        return self.manager.show_provider_info()
