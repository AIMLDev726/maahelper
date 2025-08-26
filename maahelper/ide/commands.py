"""
IDE Integration Commands for MaaHelper
Provides commands specifically designed for IDE integration
"""

import json
import sys
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core.llm_client import UnifiedLLMClient
from ..vibecoding.commands import VibecodingCommands

console = Console()

class IDECommands:
    """Commands specifically designed for IDE integration"""
    
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        self.llm_client = llm_client
        self.vibecoding = VibecodingCommands(llm_client)
    
    async def start_lsp_server(self, port: Optional[int] = None, stdio: bool = False) -> str:
        """Start the Language Server Protocol server"""
        try:
            from ..lsp.server import MaaHelperLSPServer
            
            server = MaaHelperLSPServer()
            
            if stdio:
                console.print("[green]Starting MaaHelper LSP Server with stdio...[/green]")
                server.start_stdio()
            elif port:
                console.print(f"[green]Starting MaaHelper LSP Server on port {port}...[/green]")
                server.start_server(port)
            else:
                console.print("[green]Starting MaaHelper LSP Server with stdio (default)...[/green]")
                server.start_stdio()
            
            return "✅ LSP Server started successfully"
            
        except Exception as e:
            error_msg = f"❌ Failed to start LSP server: {e}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg
    
    async def analyze_for_ide(self, file_path: str, line: Optional[int] = None, 
                             column: Optional[int] = None) -> Dict[str, Any]:
        """Analyze code for IDE integration with structured output"""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"error": f"File not found: {file_path}"}
            
            content = file_path_obj.read_text(encoding='utf-8')
            language = self._detect_language(file_path_obj.suffix)
            
            # Perform comprehensive analysis
            analysis_result = {
                "file": str(file_path_obj),
                "language": language,
                "analysis": {},
                "suggestions": [],
                "diagnostics": []
            }
            
            # Code review
            if self.llm_client:
                review_result = await self.vibecoding.code_review(
                    content, language, f"File: {file_path}"
                )
                analysis_result["analysis"]["code_review"] = review_result
                
                # Bug analysis
                bug_result = await self.vibecoding.bug_analysis(
                    content, language, f"File: {file_path}"
                )
                analysis_result["analysis"]["bug_analysis"] = bug_result
                
                # Performance analysis
                perf_result = await self.vibecoding.optimize_performance(
                    content, language, f"File: {file_path}"
                )
                analysis_result["analysis"]["performance"] = perf_result
                
                # Generate suggestions based on position if provided
                if line is not None and column is not None:
                    suggestions = await self._generate_position_suggestions(
                        content, language, line, column
                    )
                    analysis_result["suggestions"] = suggestions
            
            return analysis_result
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    async def get_completions(self, file_path: str, line: int, column: int, 
                             prefix: str = "") -> List[Dict[str, str]]:
        """Get AI-powered code completions for IDE"""
        try:
            if not self.llm_client:
                return []
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return []
            
            content = file_path_obj.read_text(encoding='utf-8')
            language = self._detect_language(file_path_obj.suffix)
            
            # Get context around the cursor
            lines = content.split('\n')
            if line >= len(lines):
                return []
            
            context_start = max(0, line - 5)
            context_end = min(len(lines), line + 5)
            context = '\n'.join(lines[context_start:context_end])
            
            prompt = f"""
            Provide code completion suggestions for {language} code.
            
            Context:
            {context}
            
            Current line: {lines[line] if line < len(lines) else ""}
            Cursor position: column {column}
            Prefix: {prefix}
            
            Return 3-5 relevant completions as JSON array:
            [{{"label": "completion", "detail": "description", "insertText": "code", "kind": "function|variable|class|keyword"}}]
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            # Parse response
            try:
                completions = json.loads(response)
                return completions if isinstance(completions, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            console.print(f"[red]Completion error: {e}[/red]")
            return []
    
    async def get_hover_info(self, file_path: str, line: int, column: int) -> Optional[str]:
        """Get hover information for symbol at position"""
        try:
            if not self.llm_client:
                return None
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None
            
            content = file_path_obj.read_text(encoding='utf-8')
            language = self._detect_language(file_path_obj.suffix)
            lines = content.split('\n')
            
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            word = self._extract_word_at_position(current_line, column)
            
            if not word:
                return None
            
            # Get context
            context_start = max(0, line - 3)
            context_end = min(len(lines), line + 4)
            context = '\n'.join(lines[context_start:context_end])
            
            prompt = f"""
            Explain the symbol '{word}' in this {language} code context:
            
            {context}
            
            Provide a brief, helpful explanation in markdown format.
            Focus on what this symbol does, its type, and usage.
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return response.strip()
            
        except Exception as e:
            console.print(f"[red]Hover error: {e}[/red]")
            return None
    
    async def get_diagnostics(self, file_path: str) -> List[Dict[str, Any]]:
        """Get diagnostics (errors, warnings, suggestions) for file"""
        try:
            if not self.llm_client:
                return []
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return []
            
            content = file_path_obj.read_text(encoding='utf-8')
            language = self._detect_language(file_path_obj.suffix)
            
            prompt = f"""
            Analyze this {language} code for issues, bugs, and improvements:
            
            {content}
            
            Return findings as JSON array:
            [{{"line": 0, "column": 0, "severity": "error|warning|info", "message": "description", "source": "maahelper"}}]
            
            Focus on:
            - Syntax errors
            - Logic bugs
            - Performance issues
            - Code quality improvements
            - Security vulnerabilities
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            try:
                diagnostics = json.loads(response)
                return diagnostics if isinstance(diagnostics, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            console.print(f"[red]Diagnostics error: {e}[/red]")
            return []
    
    async def process_stdin_request(self) -> str:
        """Process IDE request from stdin (for CLI integration)"""
        try:
            # Read JSON request from stdin
            input_data = sys.stdin.read()
            request = json.loads(input_data)
            
            command = request.get('command')
            params = request.get('params', {})
            
            result = None
            
            if command == 'analyze':
                result = await self.analyze_for_ide(
                    params.get('file'),
                    params.get('line'),
                    params.get('column')
                )
            elif command == 'completions':
                result = await self.get_completions(
                    params.get('file'),
                    params.get('line'),
                    params.get('column'),
                    params.get('prefix', '')
                )
            elif command == 'hover':
                result = await self.get_hover_info(
                    params.get('file'),
                    params.get('line'),
                    params.get('column')
                )
            elif command == 'diagnostics':
                result = await self.get_diagnostics(params.get('file'))
            else:
                result = {"error": f"Unknown command: {command}"}
            
            # Return JSON response
            response = {"result": result}
            return json.dumps(response, indent=2)
            
        except Exception as e:
            error_response = {"error": f"Request processing failed: {e}"}
            return json.dumps(error_response, indent=2)
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        return extension_map.get(file_extension.lower(), 'text')
    
    def _extract_word_at_position(self, line: str, column: int) -> str:
        """Extract word at given column position"""
        if column >= len(line):
            return ""
        
        # Find word boundaries
        start = column
        while start > 0 and (line[start-1].isalnum() or line[start-1] == '_'):
            start -= 1
        
        end = column
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        return line[start:end]
    
    async def _generate_position_suggestions(self, content: str, language: str, 
                                           line: int, column: int) -> List[Dict[str, str]]:
        """Generate suggestions based on cursor position"""
        try:
            lines = content.split('\n')
            if line >= len(lines):
                return []
            
            current_line = lines[line]
            context = '\n'.join(lines[max(0, line-2):line+3])
            
            prompt = f"""
            Analyze this {language} code and suggest improvements for line {line+1}:
            
            {context}
            
            Current cursor position: column {column}
            
            Provide 2-3 specific suggestions as JSON array:
            [{{"type": "suggestion|refactor|fix", "title": "brief title", "description": "detailed description"}}]
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            try:
                suggestions = json.loads(response)
                return suggestions if isinstance(suggestions, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            return []
