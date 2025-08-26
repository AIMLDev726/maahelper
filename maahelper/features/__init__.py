"""
MaaHelper Advanced Features
New features for version 0.0.5 including dynamic model discovery, real-time analysis, and Git integration
"""

from .model_discovery import DynamicModelDiscovery, ModelInfo, model_discovery
from .realtime_analysis import RealTimeAnalysisEngine, CodeAnalyzer, CodeIssue, realtime_analyzer
from .git_integration import GitIntegration, GitAnalyzer, CommitSuggestion, git_integration

__all__ = [
    # Model Discovery
    "DynamicModelDiscovery",
    "ModelInfo", 
    "model_discovery",
    
    # Real-time Analysis
    "RealTimeAnalysisEngine",
    "CodeAnalyzer",
    "CodeIssue",
    "realtime_analyzer",
    
    # Git Integration
    "GitIntegration",
    "GitAnalyzer", 
    "CommitSuggestion",
    "git_integration"
]
