"""
Tests for MaaHelper IDE Integration
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from maahelper.ide.commands import IDECommands
from maahelper.lsp.handlers import (
    TextDocumentHandler, CompletionHandler, DiagnosticsHandler, 
    HoverHandler, CodeActionHandler
)


class TestIDECommands:
    """Test IDE integration commands"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="AI response for IDE")
        return client
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary Python file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
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
            yield f.name
        
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def ide_commands(self, mock_llm_client):
        """IDE commands instance"""
        return IDECommands(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_analyze_for_ide(self, ide_commands, temp_file):
        """Test analyzing file for IDE integration"""
        result = await ide_commands.analyze_for_ide(temp_file)
        
        assert isinstance(result, dict)
        assert "file" in result
        assert "language" in result
        assert "analysis" in result
        assert result["language"] == "python"
        assert result["file"] == temp_file
    
    @pytest.mark.asyncio
    async def test_get_completions(self, ide_commands, temp_file):
        """Test getting code completions"""
        # Test completion at end of file
        completions = await ide_commands.get_completions(temp_file, 20, 0, "res")
        
        assert isinstance(completions, list)
        # Should return empty list or completions depending on AI response
    
    @pytest.mark.asyncio
    async def test_get_hover_info(self, ide_commands, temp_file):
        """Test getting hover information"""
        # Test hover on function name
        hover_info = await ide_commands.get_hover_info(temp_file, 1, 4)  # "hello_world"
        
        # Should return string or None
        assert hover_info is None or isinstance(hover_info, str)
    
    @pytest.mark.asyncio
    async def test_get_diagnostics(self, ide_commands, temp_file):
        """Test getting diagnostics"""
        diagnostics = await ide_commands.get_diagnostics(temp_file)
        
        assert isinstance(diagnostics, list)
        # Each diagnostic should have required fields
        for diag in diagnostics:
            if diag:  # Skip empty diagnostics
                assert "line" in diag or "message" in diag
    
    @pytest.mark.asyncio
    async def test_process_stdin_request(self, ide_commands, temp_file):
        """Test processing stdin requests"""
        # Mock stdin input
        request = {
            "command": "analyze",
            "params": {"file": temp_file}
        }
        
        with patch('sys.stdin.read', return_value=json.dumps(request)):
            result = await ide_commands.process_stdin_request()
            
            assert isinstance(result, str)
            response = json.loads(result)
            assert "result" in response
    
    def test_detect_language(self, ide_commands):
        """Test language detection from file extension"""
        assert ide_commands._detect_language('.py') == 'python'
        assert ide_commands._detect_language('.js') == 'javascript'
        assert ide_commands._detect_language('.ts') == 'typescript'
        assert ide_commands._detect_language('.java') == 'java'
        assert ide_commands._detect_language('.unknown') == 'text'
    
    def test_extract_word_at_position(self, ide_commands):
        """Test extracting word at cursor position"""
        line = "def hello_world():"
        
        # Test extracting function name
        word = ide_commands._extract_word_at_position(line, 4)
        assert word == "hello_world"
        
        # Test extracting at beginning
        word = ide_commands._extract_word_at_position(line, 0)
        assert word == "def"
        
        # Test extracting at end
        word = ide_commands._extract_word_at_position(line, len(line))
        assert word == ""


class TestLSPHandlers:
    """Test LSP handler functionality"""
    
    @pytest.fixture
    def mock_server(self):
        """Mock LSP server"""
        server = Mock()
        server._document_handler = None
        return server
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value='{"completions": []}')
        return client
    
    def test_text_document_handler(self, mock_server):
        """Test text document handler"""
        handler = TextDocumentHandler(mock_server)
        
        # Test document storage
        assert len(handler.documents) == 0
        
        # Mock document open event
        mock_params = Mock()
        mock_params.text_document.uri = "file:///test.py"
        mock_params.text_document.text = "print('hello')"
        
        # Test async method (would need proper async test setup)
        assert handler is not None
    
    def test_completion_handler(self, mock_server, mock_llm_client):
        """Test completion handler"""
        handler = CompletionHandler(mock_server, mock_llm_client)
        assert handler.server == mock_server
        assert handler.llm_client == mock_llm_client
    
    def test_diagnostics_handler(self, mock_server, mock_llm_client):
        """Test diagnostics handler"""
        handler = DiagnosticsHandler(mock_server, mock_llm_client)
        assert handler.server == mock_server
        assert handler.llm_client == mock_llm_client
        assert handler.analysis_queue is not None
    
    def test_hover_handler(self, mock_server, mock_llm_client):
        """Test hover handler"""
        handler = HoverHandler(mock_server, mock_llm_client)
        
        # Test word extraction
        word = handler._get_word_at_position("def hello_world():", 4)
        assert word == "hello_world"
        
        # Test range calculation
        range_info = handler._get_word_range("def hello_world():", 4, "hello_world")
        assert "start" in range_info
        assert "end" in range_info
    
    def test_code_action_handler(self, mock_server, mock_llm_client):
        """Test code action handler"""
        handler = CodeActionHandler(mock_server, mock_llm_client)
        
        # Test text extraction
        text = "line1\nline2\nline3"
        mock_range = Mock()
        mock_range.start.line = 0
        mock_range.start.character = 0
        mock_range.end.line = 1
        mock_range.end.character = 5
        
        extracted = handler._extract_range_text(text, mock_range)
        assert "line1" in extracted


class TestLSPIntegration:
    """Integration tests for LSP functionality"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for integration tests"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="LSP integration response")
        return client
    
    @pytest.mark.asyncio
    async def test_lsp_server_creation(self, mock_llm_client):
        """Test LSP server creation and initialization"""
        # Import here to avoid issues if pygls not available
        try:
            from maahelper.lsp.server import MaaHelperLSPServer
            
            server = MaaHelperLSPServer()
            assert server is not None
            assert server.llm_client is None  # Not initialized yet
            
        except ImportError:
            # Skip test if pygls not available
            pytest.skip("pygls not available")
    
    @pytest.mark.asyncio
    async def test_ide_commands_integration(self, mock_llm_client):
        """Test IDE commands integration with real file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / "integration_test.py"
            test_file.write_text("""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test the function
result = factorial(5)
print(f"Factorial of 5 is {result}")
""")
            
            ide_commands = IDECommands(mock_llm_client)
            
            # Test file analysis
            analysis = await ide_commands.analyze_for_ide(str(test_file))
            assert analysis["language"] == "python"
            assert "factorial" in analysis["content"]
            
            # Test diagnostics
            diagnostics = await ide_commands.get_diagnostics(str(test_file))
            assert isinstance(diagnostics, list)


class TestErrorHandling:
    """Test error handling in IDE integration"""
    
    @pytest.fixture
    def ide_commands_no_llm(self):
        """IDE commands without LLM client"""
        return IDECommands(None)
    
    @pytest.mark.asyncio
    async def test_no_llm_client_handling(self, ide_commands_no_llm):
        """Test handling when no LLM client is available"""
        # These should handle gracefully without LLM client
        completions = await ide_commands_no_llm.get_completions("nonexistent.py", 0, 0)
        assert completions == []
        
        hover = await ide_commands_no_llm.get_hover_info("nonexistent.py", 0, 0)
        assert hover is None
        
        diagnostics = await ide_commands_no_llm.get_diagnostics("nonexistent.py")
        assert diagnostics == []
    
    @pytest.mark.asyncio
    async def test_file_not_found_handling(self):
        """Test handling of non-existent files"""
        mock_client = Mock()
        mock_client.achat_completion = AsyncMock(return_value="response")
        
        ide_commands = IDECommands(mock_client)
        
        # Test with non-existent file
        result = await ide_commands.analyze_for_ide("nonexistent_file.py")
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_position_handling(self):
        """Test handling of invalid cursor positions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("short file")
            temp_file = f.name
        
        try:
            mock_client = Mock()
            mock_client.achat_completion = AsyncMock(return_value="response")
            ide_commands = IDECommands(mock_client)
            
            # Test with invalid line number
            hover = await ide_commands.get_hover_info(temp_file, 1000, 0)
            assert hover is None
            
            completions = await ide_commands.get_completions(temp_file, 1000, 0)
            assert completions == []
            
        finally:
            Path(temp_file).unlink(missing_ok=True)


class TestPerformance:
    """Performance tests for IDE integration"""
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self):
        """Test handling of large files"""
        # Create a large test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write a large file (1000 lines)
            for i in range(1000):
                f.write(f"def function_{i}():\n    return {i}\n\n")
            temp_file = f.name
        
        try:
            mock_client = Mock()
            mock_client.achat_completion = AsyncMock(return_value="response")
            ide_commands = IDECommands(mock_client)
            
            # Test analysis of large file
            import time
            start_time = time.time()
            
            result = await ide_commands.analyze_for_ide(temp_file)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert processing_time < 10.0  # 10 seconds max
            assert "language" in result
            
        finally:
            Path(temp_file).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent IDE requests"""
        mock_client = Mock()
        mock_client.achat_completion = AsyncMock(return_value="concurrent response")
        ide_commands = IDECommands(mock_client)
        
        # Create multiple temporary files
        temp_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f"def test_function_{i}(): pass")
                temp_files.append(f.name)
        
        try:
            # Run concurrent analysis
            tasks = [
                ide_commands.analyze_for_ide(temp_file) 
                for temp_file in temp_files
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should complete successfully
            assert len(results) == 5
            for result in results:
                assert "language" in result
                
        finally:
            # Cleanup
            for temp_file in temp_files:
                Path(temp_file).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
