#!/usr/bin/env python3
"""
Comprehensive Import Testing Suite for MaaHelper
Tests all module imports, dependencies, and circular import issues
"""

import pytest
import sys
import importlib
import pkgutil
from pathlib import Path
from unittest.mock import patch, Mock
from typing import List, Dict, Set, Any

# Core modules that should always be importable
CORE_MODULES = [
    "maahelper",
    "maahelper.core",
    "maahelper.core.llm_client",
    "maahelper.utils",
    "maahelper.utils.streaming",
    "maahelper.utils.logging_system",
    "maahelper.utils.memory_manager",
    "maahelper.utils.rate_limiter",
    "maahelper.utils.input_validator",
    "maahelper.managers",
    "maahelper.managers.streamlined_api_key_manager",
    "maahelper.managers.advanced_api_key_manager",
    "maahelper.config",
    "maahelper.config.config_manager"
]

# Optional modules that may have external dependencies
OPTIONAL_MODULES = [
    "maahelper.lsp",
    "maahelper.lsp.server",
    "maahelper.lsp.handlers",
    "maahelper.features.git_integration",
    "maahelper.features.model_discovery",
    "maahelper.features.realtime_analysis"
]

# CLI modules
CLI_MODULES = [
    "maahelper.cli",
    "maahelper.cli.modern_enhanced_cli",
    "maahelper.cli.modern_cli_selector",
    "maahelper.cli_entry"
]

# Workflow and IDE modules
WORKFLOW_MODULES = [
    "maahelper.workflows",
    "maahelper.workflows.engine",
    "maahelper.workflows.commands",
    "maahelper.workflows.templates",
    "maahelper.workflows.state",
    "maahelper.workflows.nodes",
    "maahelper.ide",
    "maahelper.ide.commands",
    "maahelper.vibecoding",
    "maahelper.vibecoding.commands",
    "maahelper.vibecoding.workflow",
    "maahelper.vibecoding.prompts"
]

class TestCoreImports:
    """Test core module imports that should always work"""
    
    @pytest.mark.parametrize("module_name", CORE_MODULES)
    def test_core_module_import(self, module_name):
        """Test that core modules can be imported without errors"""
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import core module {module_name}: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing {module_name}: {e}")
    
    def test_main_package_import(self):
        """Test main package import and basic functionality"""
        try:
            import maahelper
            
            # Check version is available
            assert hasattr(maahelper, '__version__')
            assert isinstance(maahelper.__version__, str)
            
            # Check core exports are available
            expected_exports = [
                'UnifiedLLMClient',
                'create_llm_client',
                'get_all_providers',
                'get_provider_models'
            ]
            
            for export in expected_exports:
                assert hasattr(maahelper, export), f"Missing export: {export}"
                
        except ImportError as e:
            pytest.fail(f"Failed to import main maahelper package: {e}")
    
    def test_llm_client_imports(self):
        """Test LLM client imports and basic functionality"""
        try:
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
            
            # Test basic functionality
            providers = get_all_providers()
            assert isinstance(providers, list)
            assert len(providers) > 0
            
            # Test config creation
            config = LLMConfig(provider="openai", model="gpt-4o", api_key="test")
            assert config.provider == "openai"
            assert config.model == "gpt-4o"
            
        except ImportError as e:
            pytest.fail(f"Failed to import LLM client components: {e}")


class TestOptionalImports:
    """Test optional module imports that may have external dependencies"""
    
    @pytest.mark.parametrize("module_name", OPTIONAL_MODULES)
    def test_optional_module_import(self, module_name):
        """Test optional modules - should either import or fail gracefully"""
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            # Optional modules may fail due to missing dependencies
            # This is acceptable, but we should log it
            print(f"Optional module {module_name} not available: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing optional module {module_name}: {e}")
    
    def test_lsp_server_import_with_missing_deps(self):
        """Test LSP server import when pygls is not available"""
        with patch.dict('sys.modules', {'pygls': None, 'lsprotocol': None}):
            try:
                from maahelper.lsp import server
                # Should handle missing dependencies gracefully
            except ImportError:
                # Expected when dependencies are missing
                pass
            except Exception as e:
                pytest.fail(f"LSP server should handle missing dependencies gracefully: {e}")
    
    def test_git_integration_import(self):
        """Test git integration import"""
        try:
            from maahelper.features.git_integration import GitIntegration
            # Should be importable if gitpython is available
        except ImportError as e:
            # May fail if gitpython not available
            print(f"Git integration not available: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing git integration: {e}")


class TestCLIImports:
    """Test CLI module imports"""
    
    @pytest.mark.parametrize("module_name", CLI_MODULES)
    def test_cli_module_import(self, module_name):
        """Test CLI module imports"""
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import CLI module {module_name}: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing CLI module {module_name}: {e}")
    
    def test_cli_entry_point_imports(self):
        """Test CLI entry point imports"""
        try:
            from maahelper.cli_entry import main
            assert callable(main)
            
            from maahelper.cli.modern_enhanced_cli import main as enhanced_main
            assert callable(enhanced_main)
            
            from maahelper.cli.modern_cli_selector import main as selector_main
            assert callable(selector_main)
            
        except ImportError as e:
            pytest.fail(f"Failed to import CLI entry points: {e}")


class TestWorkflowImports:
    """Test workflow and IDE module imports"""
    
    @pytest.mark.parametrize("module_name", WORKFLOW_MODULES)
    def test_workflow_module_import(self, module_name):
        """Test workflow module imports"""
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import workflow module {module_name}: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing workflow module {module_name}: {e}")
    
    def test_workflow_engine_import(self):
        """Test workflow engine specific imports"""
        try:
            from maahelper.workflows.engine import WorkflowEngine, WorkflowDefinition
            from maahelper.workflows.templates import WorkflowTemplates
            from maahelper.workflows.state import WorkflowStateManager
            from maahelper.workflows.nodes import WorkflowNodes
            
            # Test basic instantiation
            templates = WorkflowTemplates()
            assert templates is not None
            
        except ImportError as e:
            pytest.fail(f"Failed to import workflow engine components: {e}")


class TestCircularImports:
    """Test for circular import issues"""
    
    def test_no_circular_imports_in_core(self):
        """Test that core modules don't have circular imports"""
        # Import core modules in different orders to detect circular imports
        import_orders = [
            ["maahelper.core.llm_client", "maahelper.utils.streaming"],
            ["maahelper.utils.streaming", "maahelper.core.llm_client"],
            ["maahelper.managers.streamlined_api_key_manager", "maahelper.config.config_manager"],
            ["maahelper.config.config_manager", "maahelper.managers.streamlined_api_key_manager"]
        ]
        
        for order in import_orders:
            # Clear modules from cache
            for module in order:
                if module in sys.modules:
                    del sys.modules[module]
            
            try:
                for module in order:
                    importlib.import_module(module)
            except ImportError as e:
                if "circular import" in str(e).lower():
                    pytest.fail(f"Circular import detected: {e}")
    
    def test_cli_import_independence(self):
        """Test that CLI modules can be imported independently"""
        cli_modules = [
            "maahelper.cli.modern_enhanced_cli",
            "maahelper.cli.modern_cli_selector",
            "maahelper.cli_entry"
        ]
        
        for module in cli_modules:
            # Clear module cache
            if module in sys.modules:
                del sys.modules[module]
            
            try:
                importlib.import_module(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module} independently: {e}")


class TestDependencyChecks:
    """Test dependency availability and version compatibility"""
    
    def test_required_dependencies(self):
        """Test that required dependencies are available"""
        required_deps = [
            "openai",
            "rich", 
            "cryptography",
            "keyring",
            "structlog",
            "click",
            "python-dotenv",
            "PyYAML",
            "aiohttp",
            "aiofiles",
            "chardet",
            "tiktoken",
            "watchdog",
            "gitpython",
            "requests",
            "beautifulsoup4"
        ]
        
        missing_deps = []
        
        for dep in required_deps:
            try:
                importlib.import_module(dep.replace("-", "_"))
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            pytest.fail(f"Missing required dependencies: {missing_deps}")
    
    def test_optional_dependencies(self):
        """Test optional dependencies and log their availability"""
        optional_deps = [
            ("pygls", "LSP server functionality"),
            ("lsprotocol", "LSP protocol support"),
            ("groq", "Groq AI provider"),
            ("anthropic", "Anthropic AI provider"),
            ("google.generativeai", "Google AI provider"),
            ("g4f", "GPT4Free provider")
        ]
        
        available_optional = []
        missing_optional = []
        
        for dep, description in optional_deps:
            try:
                importlib.import_module(dep)
                available_optional.append((dep, description))
            except ImportError:
                missing_optional.append((dep, description))
        
        print(f"\nOptional dependencies available: {len(available_optional)}")
        for dep, desc in available_optional:
            print(f"  ✓ {dep}: {desc}")
        
        print(f"\nOptional dependencies missing: {len(missing_optional)}")
        for dep, desc in missing_optional:
            print(f"  ✗ {dep}: {desc}")


class TestModuleStructure:
    """Test module structure and organization"""
    
    def test_package_structure(self):
        """Test that package structure is correct"""
        maahelper_path = Path(__file__).parent.parent / "maahelper"
        assert maahelper_path.exists(), "maahelper package directory not found"
        
        expected_dirs = [
            "cli", "core", "utils", "managers", "config",
            "workflows", "ide", "lsp", "features", "vibecoding"
        ]
        
        missing_dirs = []
        for dir_name in expected_dirs:
            dir_path = maahelper_path / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            pytest.fail(f"Missing package directories: {missing_dirs}")
    
    def test_init_files_exist(self):
        """Test that __init__.py files exist in all packages"""
        maahelper_path = Path(__file__).parent.parent / "maahelper"
        
        for root, dirs, files in maahelper_path.rglob("*"):
            if root.is_dir() and any(f.suffix == ".py" for f in root.iterdir() if f.is_file()):
                init_file = root / "__init__.py"
                if not init_file.exists():
                    pytest.fail(f"Missing __init__.py in {root}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
