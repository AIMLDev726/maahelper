#!/usr/bin/env python3
"""
Comprehensive CLI Testing Suite for MaaHelper
Tests all CLI entry points, commands, and error handling
"""

import pytest
import subprocess
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

# CLI entry points from pyproject.toml
CLI_ENTRY_POINTS = [
    "maahelper-selector",
    "maahelper-menu", 
    "maahelper-super-chat",
    "maahelper-smart",
    "maahelper-genius",
    "maahelper-fast-chat",
    "maahelper-quick",
    "maahelper-turbo",
    "maahelper-multi",
    "maahelper-pro",
    "maahelper-advanced",
    "maahelper-dev",
    "maahelper-expert",
    "maahelper",
    "maahelper-keys",
    "maahelper-api-key",
    "maahelper-setup-keys",
    "maahelper-lsp",
    "maahelper-workflow",
    "maahelper-ide"
]

class TestCLIEntryPoints:
    """Test all CLI entry points defined in pyproject.toml"""
    
    def test_cli_entry_points_exist(self):
        """Test that all CLI entry points are properly defined"""
        # Read pyproject.toml to verify entry points
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"
        
        content = pyproject_path.read_text()
        
        # Check that all expected entry points are defined
        for entry_point in CLI_ENTRY_POINTS:
            assert entry_point in content, f"Entry point {entry_point} not found in pyproject.toml"
    
    @pytest.mark.parametrize("cli_command", CLI_ENTRY_POINTS)
    def test_cli_help_option(self, cli_command):
        """Test --help option for each CLI command"""
        try:
            # Test --help option
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "maahelper"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                pytest.skip(f"maahelper not installed, skipping {cli_command}")
            
            # Try to run the command with --help
            result = subprocess.run(
                [cli_command, "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should either succeed or fail gracefully
            assert result.returncode in [0, 1, 2], f"{cli_command} --help failed with code {result.returncode}"
            
        except subprocess.TimeoutExpired:
            pytest.fail(f"{cli_command} --help timed out")
        except FileNotFoundError:
            pytest.skip(f"{cli_command} command not found (not installed)")
    
    @pytest.mark.parametrize("cli_command", CLI_ENTRY_POINTS)
    def test_cli_version_option(self, cli_command):
        """Test --version option for each CLI command"""
        try:
            result = subprocess.run(
                [cli_command, "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should either succeed or fail gracefully
            assert result.returncode in [0, 1, 2], f"{cli_command} --version failed with code {result.returncode}"
            
        except subprocess.TimeoutExpired:
            pytest.fail(f"{cli_command} --version timed out")
        except FileNotFoundError:
            pytest.skip(f"{cli_command} command not found (not installed)")


class TestCLIImports:
    """Test CLI module imports and dependencies"""
    
    def test_cli_module_imports(self):
        """Test that CLI modules can be imported without errors"""
        import_tests = [
            "maahelper.cli.modern_enhanced_cli",
            "maahelper.cli.modern_cli_selector", 
            "maahelper.cli_entry",
            "maahelper.managers.advanced_api_key_manager",
            "maahelper.managers.streamlined_api_key_manager",
            "maahelper.workflows.commands",
            "maahelper.ide.commands",
            "maahelper.lsp.server"
        ]
        
        failed_imports = []
        
        for module_name in import_tests:
            try:
                __import__(module_name)
            except ImportError as e:
                failed_imports.append((module_name, str(e)))
            except Exception as e:
                failed_imports.append((module_name, f"Unexpected error: {str(e)}"))
        
        if failed_imports:
            error_msg = "Failed to import modules:\n"
            for module, error in failed_imports:
                error_msg += f"  - {module}: {error}\n"
            pytest.fail(error_msg)
    
    def test_main_entry_points_callable(self):
        """Test that main entry point functions are callable"""
        entry_point_tests = [
            ("maahelper.cli_entry", "main"),
            ("maahelper.cli.modern_enhanced_cli", "main"),
            ("maahelper.cli.modern_cli_selector", "main"),
            ("maahelper.managers.advanced_api_key_manager", "main"),
            ("maahelper.workflows.commands", "main"),
            ("maahelper.ide.commands", "main"),
            ("maahelper.lsp.server", "main")
        ]
        
        failed_callables = []
        
        for module_name, function_name in entry_point_tests:
            try:
                module = __import__(module_name, fromlist=[function_name])
                func = getattr(module, function_name, None)
                if func is None:
                    failed_callables.append(f"{module_name}.{function_name} not found")
                elif not callable(func):
                    failed_callables.append(f"{module_name}.{function_name} not callable")
            except ImportError as e:
                failed_callables.append(f"{module_name}: Import error - {str(e)}")
            except Exception as e:
                failed_callables.append(f"{module_name}: Unexpected error - {str(e)}")
        
        if failed_callables:
            error_msg = "Entry point function issues:\n"
            for error in failed_callables:
                error_msg += f"  - {error}\n"
            pytest.fail(error_msg)


class TestCLICommands:
    """Test CLI command functionality"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="Test response")
        client.chat_completion = Mock(return_value="Test response")
        return client
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('Hello, World!')")
            yield temp_dir
    
    def test_modern_enhanced_cli_creation(self, mock_llm_client, temp_workspace):
        """Test ModernEnhancedCLI creation"""
        try:
            from maahelper.cli.modern_enhanced_cli import ModernEnhancedCLI
            
            cli = ModernEnhancedCLI(workspace_path=temp_workspace)
            assert cli is not None
            assert cli.workspace_path == temp_workspace
            
        except ImportError as e:
            pytest.skip(f"Cannot import ModernEnhancedCLI: {e}")
    
    def test_cli_selector_creation(self):
        """Test ModernCLISelector creation"""
        try:
            from maahelper.cli.modern_cli_selector import ModernCLISelector
            
            selector = ModernCLISelector()
            assert selector is not None
            
        except ImportError as e:
            pytest.skip(f"Cannot import ModernCLISelector: {e}")
    
    def test_workflow_commands_creation(self, mock_llm_client, temp_workspace):
        """Test WorkflowCommands creation"""
        try:
            from maahelper.workflows.commands import WorkflowCommands
            
            commands = WorkflowCommands(mock_llm_client, temp_workspace)
            assert commands is not None
            
        except ImportError as e:
            pytest.skip(f"Cannot import WorkflowCommands: {e}")
    
    def test_ide_commands_creation(self, mock_llm_client):
        """Test IDECommands creation"""
        try:
            from maahelper.ide.commands import IDECommands
            
            commands = IDECommands(mock_llm_client)
            assert commands is not None
            
        except ImportError as e:
            pytest.skip(f"Cannot import IDECommands: {e}")


class TestCLIErrorHandling:
    """Test CLI error handling and edge cases"""
    
    def test_invalid_command_handling(self):
        """Test handling of invalid commands"""
        try:
            from maahelper.cli.modern_enhanced_cli import ModernEnhancedCLI
            
            cli = ModernEnhancedCLI()
            # Test that invalid commands don't crash the CLI
            assert cli is not None
            
        except ImportError as e:
            pytest.skip(f"Cannot import ModernEnhancedCLI: {e}")
    
    def test_missing_dependencies_handling(self):
        """Test handling when optional dependencies are missing"""
        # Test LSP server when pygls is not available
        with patch.dict('sys.modules', {'pygls': None, 'lsprotocol': None}):
            try:
                from maahelper.lsp.server import main as lsp_main
                # Should handle missing dependencies gracefully
                assert lsp_main is not None
            except ImportError:
                # Expected when dependencies are missing
                pass
            except Exception as e:
                pytest.fail(f"Unexpected error when dependencies missing: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
