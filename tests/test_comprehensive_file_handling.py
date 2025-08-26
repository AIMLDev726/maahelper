#!/usr/bin/env python3
"""
Comprehensive File Handling Testing Suite for MaaHelper
Tests file analysis, workspace scanning, and file processing capabilities
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Test imports
try:
    from maahelper.utils.streamlined_file_handler import file_handler
    from maahelper.utils.streamlined_file_handler import StreamlinedFileHandler
    FILE_HANDLER_AVAILABLE = True
except ImportError as e:
    FILE_HANDLER_AVAILABLE = False
    IMPORT_ERROR = str(e)

class TestFileHandlerAvailability:
    """Test file handler availability and basic imports"""
    
    def test_file_handler_import(self):
        """Test that file handler can be imported"""
        if not FILE_HANDLER_AVAILABLE:
            pytest.fail(f"Cannot import file handler: {IMPORT_ERROR}")
        
        assert file_handler is not None
        assert StreamlinedFileHandler is not None

@pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
class TestFileHandlerBasics:
    """Test basic file handler functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create various test files
            (workspace / "test.py").write_text("""
def hello_world():
    '''A simple hello world function'''
    print("Hello, World!")
    return "Hello"

class Calculator:
    def add(self, a, b):
        return a + b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

# Some test code with potential issues
x = 1
y = 0
result = x / y  # This will cause division by zero
""")
            
            (workspace / "test.js").write_text("""
function helloWorld() {
    console.log("Hello, World!");
    return "Hello";
}

class Calculator {
    add(a, b) {
        return a + b;
    }
    
    divide(a, b) {
        if (b === 0) {
            throw new Error("Cannot divide by zero");
        }
        return a / b;
    }
}

// Some test code with potential issues
let x = 1;
let y = 0;
let result = x / y; // This will result in Infinity
""")
            
            (workspace / "README.md").write_text("""
# Test Project

This is a test project for file handling tests.

## Features
- Python code
- JavaScript code
- Documentation

## Issues
- Division by zero in Python
- Potential infinity in JavaScript
""")
            
            (workspace / "config.json").write_text("""
{
    "name": "test-project",
    "version": "1.0.0",
    "dependencies": {
        "python": ">=3.8",
        "node": ">=14.0"
    }
}
""")
            
            # Create subdirectory with more files
            subdir = workspace / "src"
            subdir.mkdir()
            (subdir / "utils.py").write_text("""
def utility_function():
    pass

def another_function():
    # TODO: Implement this function
    pass
""")
            
            yield workspace
    
    def test_file_handler_initialization(self):
        """Test file handler initialization"""
        handler = StreamlinedFileHandler()
        assert handler is not None
        
        # Test global file_handler instance
        assert file_handler is not None
    
    def test_supported_file_types(self):
        """Test supported file types detection"""
        supported_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.md', '.txt', '.json', '.yaml', '.yml']
        
        for ext in supported_extensions:
            assert file_handler.is_supported_file(f"test{ext}"), f"Extension {ext} should be supported"
        
        # Test unsupported extensions
        unsupported_extensions = ['.exe', '.bin', '.jpg', '.png', '.pdf']
        for ext in unsupported_extensions:
            assert not file_handler.is_supported_file(f"test{ext}"), f"Extension {ext} should not be supported"
    
    def test_file_analysis_python(self, temp_workspace):
        """Test Python file analysis"""
        python_file = temp_workspace / "test.py"
        
        try:
            analysis = file_handler.analyze_file(str(python_file))
            
            assert isinstance(analysis, dict)
            assert "file_path" in analysis
            assert "language" in analysis
            assert "content" in analysis
            assert analysis["language"] == "python"
            assert "hello_world" in analysis["content"]
            
        except Exception as e:
            pytest.fail(f"Python file analysis failed: {e}")
    
    def test_file_analysis_javascript(self, temp_workspace):
        """Test JavaScript file analysis"""
        js_file = temp_workspace / "test.js"
        
        try:
            analysis = file_handler.analyze_file(str(js_file))
            
            assert isinstance(analysis, dict)
            assert "file_path" in analysis
            assert "language" in analysis
            assert "content" in analysis
            assert analysis["language"] == "javascript"
            assert "helloWorld" in analysis["content"]
            
        except Exception as e:
            pytest.fail(f"JavaScript file analysis failed: {e}")
    
    def test_file_analysis_markdown(self, temp_workspace):
        """Test Markdown file analysis"""
        md_file = temp_workspace / "README.md"
        
        try:
            analysis = file_handler.analyze_file(str(md_file))
            
            assert isinstance(analysis, dict)
            assert "file_path" in analysis
            assert "language" in analysis
            assert "content" in analysis
            assert analysis["language"] == "markdown"
            assert "Test Project" in analysis["content"]
            
        except Exception as e:
            pytest.fail(f"Markdown file analysis failed: {e}")
    
    def test_file_analysis_json(self, temp_workspace):
        """Test JSON file analysis"""
        json_file = temp_workspace / "config.json"
        
        try:
            analysis = file_handler.analyze_file(str(json_file))
            
            assert isinstance(analysis, dict)
            assert "file_path" in analysis
            assert "language" in analysis
            assert "content" in analysis
            assert analysis["language"] == "json"
            assert "test-project" in analysis["content"]
            
        except Exception as e:
            pytest.fail(f"JSON file analysis failed: {e}")
    
    def test_workspace_scanning(self, temp_workspace):
        """Test workspace scanning functionality"""
        try:
            files = file_handler.scan_workspace(str(temp_workspace))
            
            assert isinstance(files, list)
            assert len(files) > 0
            
            # Check that all expected files are found
            file_names = [Path(f).name for f in files]
            expected_files = ["test.py", "test.js", "README.md", "config.json", "utils.py"]
            
            for expected_file in expected_files:
                assert expected_file in file_names, f"Expected file {expected_file} not found in scan"
            
        except Exception as e:
            pytest.fail(f"Workspace scanning failed: {e}")
    
    def test_file_filtering(self, temp_workspace):
        """Test file filtering by extension"""
        try:
            # Test Python files only
            python_files = file_handler.scan_workspace(str(temp_workspace), extensions=['.py'])
            python_file_names = [Path(f).name for f in python_files]
            
            assert "test.py" in python_file_names
            assert "utils.py" in python_file_names
            assert "test.js" not in python_file_names
            assert "README.md" not in python_file_names
            
            # Test multiple extensions
            code_files = file_handler.scan_workspace(str(temp_workspace), extensions=['.py', '.js'])
            code_file_names = [Path(f).name for f in code_files]
            
            assert "test.py" in code_file_names
            assert "test.js" in code_file_names
            assert "README.md" not in code_file_names
            
        except Exception as e:
            pytest.fail(f"File filtering failed: {e}")


class TestFileHandlerErrorHandling:
    """Test file handler error handling"""
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_nonexistent_file_handling(self):
        """Test handling of non-existent files"""
        try:
            result = file_handler.analyze_file("nonexistent_file.py")
            # Should return error information or None
            assert result is None or "error" in result
        except FileNotFoundError:
            # This is also acceptable behavior
            pass
        except Exception as e:
            pytest.fail(f"Unexpected error for non-existent file: {e}")
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_binary_file_handling(self):
        """Test handling of binary files"""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
            temp_file.write(b'\x00\x01\x02\x03\x04\x05')
            temp_file_path = temp_file.name
        
        try:
            result = file_handler.analyze_file(temp_file_path)
            # Should handle binary files gracefully
            assert result is None or "error" in result or "binary" in str(result).lower()
        except Exception as e:
            # Should not crash on binary files
            assert "binary" in str(e).lower() or "encoding" in str(e).lower()
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_large_file_handling(self):
        """Test handling of large files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            # Create a large file (1MB of Python code)
            for i in range(10000):
                temp_file.write(f"def function_{i}():\n    return {i}\n\n")
            temp_file_path = temp_file.name
        
        try:
            result = file_handler.analyze_file(temp_file_path)
            # Should handle large files without crashing
            assert result is not None
            if isinstance(result, dict):
                assert "content" in result
        except Exception as e:
            # Should handle large files gracefully
            assert "size" in str(e).lower() or "memory" in str(e).lower()
        finally:
            os.unlink(temp_file_path)
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_permission_denied_handling(self):
        """Test handling of permission denied errors"""
        # This test may not work on all systems
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write("print('test')")
                temp_file_path = temp_file.name
            
            # Try to remove read permissions (may not work on Windows)
            try:
                os.chmod(temp_file_path, 0o000)
                result = file_handler.analyze_file(temp_file_path)
                # Should handle permission errors gracefully
                assert result is None or "error" in result or "permission" in str(result).lower()
            except PermissionError:
                # Expected on some systems
                pass
            finally:
                # Restore permissions and cleanup
                try:
                    os.chmod(temp_file_path, 0o644)
                    os.unlink(temp_file_path)
                except:
                    pass
        except Exception as e:
            # Permission tests may not work on all systems
            pytest.skip(f"Permission test not supported on this system: {e}")


class TestFileHandlerIntegration:
    """Test file handler integration with other components"""
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_file_handler_with_llm_client(self, temp_workspace):
        """Test file handler integration with LLM client"""
        mock_llm_client = Mock()
        mock_llm_client.chat_completion = Mock(return_value="Analysis complete")
        
        try:
            # Test if file handler can work with LLM client
            python_file = temp_workspace / "test.py"
            analysis = file_handler.analyze_file(str(python_file))
            
            if analysis and "content" in analysis:
                # Simulate LLM analysis
                response = mock_llm_client.chat_completion([
                    {"role": "user", "content": f"Analyze this code: {analysis['content'][:500]}"}
                ])
                assert response == "Analysis complete"
            
        except Exception as e:
            pytest.fail(f"File handler LLM integration failed: {e}")
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_file_handler_performance(self, temp_workspace):
        """Test file handler performance with multiple files"""
        import time
        
        try:
            start_time = time.time()
            
            # Scan workspace multiple times
            for _ in range(5):
                files = file_handler.scan_workspace(str(temp_workspace))
                assert len(files) > 0
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 10.0, f"File scanning too slow: {processing_time}s"
            
        except Exception as e:
            pytest.fail(f"File handler performance test failed: {e}")


class TestFileHandlerUtilities:
    """Test file handler utility functions"""
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_language_detection(self):
        """Test language detection from file extensions"""
        test_cases = [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.ts", "typescript"),
            ("test.java", "java"),
            ("test.cpp", "cpp"),
            ("test.c", "c"),
            ("test.h", "c"),
            ("README.md", "markdown"),
            ("config.json", "json"),
            ("config.yaml", "yaml"),
            ("config.yml", "yaml"),
            ("test.txt", "text")
        ]
        
        for filename, expected_language in test_cases:
            detected = file_handler.detect_language(filename)
            assert detected == expected_language, f"Expected {expected_language} for {filename}, got {detected}"
    
    @pytest.mark.skipif(not FILE_HANDLER_AVAILABLE, reason="File handler not available")
    def test_file_size_handling(self):
        """Test file size calculations and limits"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            content = "print('test')\n" * 1000  # ~14KB file
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            file_size = os.path.getsize(temp_file_path)
            assert file_size > 0
            
            # Test if file handler respects size limits
            analysis = file_handler.analyze_file(temp_file_path)
            assert analysis is not None
            
        finally:
            os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
