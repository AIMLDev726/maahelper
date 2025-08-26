"""
LSP Handlers for MaaHelper
Implements various LSP features like completion, diagnostics, hover, etc.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TextDocumentHandler:
    """Handles text document lifecycle events"""
    
    def __init__(self, server):
        self.server = server
        self.documents: Dict[str, str] = {}
    
    async def did_open(self, params):
        """Handle document open"""
        uri = params.text_document.uri
        text = params.text_document.text
        self.documents[uri] = text
        logger.info(f"Document opened: {uri}")
    
    async def did_change(self, params):
        """Handle document change"""
        uri = params.text_document.uri
        changes = params.content_changes
        
        # Apply changes (simplified - assumes full document updates)
        if changes and hasattr(changes[0], 'text'):
            self.documents[uri] = changes[0].text
    
    async def did_save(self, params):
        """Handle document save"""
        uri = params.text_document.uri
        logger.info(f"Document saved: {uri}")
    
    async def did_close(self, params):
        """Handle document close"""
        uri = params.text_document.uri
        if uri in self.documents:
            del self.documents[uri]
        logger.info(f"Document closed: {uri}")

class CompletionHandler:
    """Provides AI-powered code completion"""
    
    def __init__(self, server, llm_client):
        self.server = server
        self.llm_client = llm_client
    
    async def provide_completion(self, params):
        """Provide completion suggestions"""
        if not self.llm_client:
            return None
        
        try:
            uri = params.text_document.uri
            position = params.position
            
            # Get document content
            document_handler = getattr(self.server, '_document_handler', None)
            if not document_handler or uri not in document_handler.documents:
                return None
            
            text = document_handler.documents[uri]
            lines = text.split('\n')
            
            if position.line >= len(lines):
                return None
            
            current_line = lines[position.line]
            prefix = current_line[:position.character]
            
            # Generate completion using AI
            completion_items = await self._generate_ai_completions(
                text, position.line, position.character, prefix
            )
            
            return {"items": completion_items, "isIncomplete": False}
            
        except Exception as e:
            logger.error(f"Completion error: {e}")
            return None
    
    async def _generate_ai_completions(self, text: str, line: int, char: int, prefix: str) -> List[Dict]:
        """Generate AI-powered completions"""
        try:
            # Create context for AI
            context_lines = text.split('\n')[max(0, line-5):line+1]
            context = '\n'.join(context_lines)
            
            prompt = f"""
            Provide code completion suggestions for the following context:
            
            Context:
            {context}
            
            Current line prefix: {prefix}
            
            Suggest 3-5 relevant completions. Return as JSON array with format:
            [{{"label": "suggestion", "detail": "description", "insertText": "code"}}]
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            # Parse AI response (simplified)
            import json
            try:
                completions = json.loads(response)
                return completions if isinstance(completions, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"AI completion generation error: {e}")
            return []

class DiagnosticsHandler:
    """Provides AI-powered code diagnostics"""
    
    def __init__(self, server, llm_client):
        self.server = server
        self.llm_client = llm_client
        self.analysis_queue = asyncio.Queue()
        self.background_task = None
    
    async def start_background_analysis(self):
        """Start background analysis task"""
        self.background_task = asyncio.create_task(self._background_analyzer())
    
    async def stop_background_analysis(self):
        """Stop background analysis task"""
        if self.background_task:
            self.background_task.cancel()
    
    async def _background_analyzer(self):
        """Background task for analyzing documents"""
        while True:
            try:
                uri = await self.analysis_queue.get()
                await self._analyze_document_internal(uri)
                self.analysis_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background analysis error: {e}")
    
    async def analyze_document(self, uri: str):
        """Queue document for analysis"""
        await self.analysis_queue.put(uri)
    
    async def _analyze_document_internal(self, uri: str):
        """Perform actual document analysis"""
        if not self.llm_client:
            return
        
        try:
            document_handler = getattr(self.server, '_document_handler', None)
            if not document_handler or uri not in document_handler.documents:
                return
            
            text = document_handler.documents[uri]
            diagnostics = await self._generate_ai_diagnostics(text, uri)
            
            # Send diagnostics to client (simplified)
            logger.info(f"Generated {len(diagnostics)} diagnostics for {uri}")
            
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
    
    async def _generate_ai_diagnostics(self, text: str, uri: str) -> List[Dict]:
        """Generate AI-powered diagnostics"""
        try:
            prompt = f"""
            Analyze the following code for potential issues, bugs, and improvements:
            
            {text}
            
            Return findings as JSON array with format:
            [{{"line": 0, "column": 0, "severity": "error|warning|info", "message": "description"}}]
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            # Parse AI response
            import json
            try:
                diagnostics = json.loads(response)
                return diagnostics if isinstance(diagnostics, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"AI diagnostics generation error: {e}")
            return []
    
    async def provide_diagnostics(self, params):
        """Provide diagnostics for a document"""
        uri = params.text_document.uri
        await self._analyze_document_internal(uri)
        return []

class HoverHandler:
    """Provides AI-powered hover information"""
    
    def __init__(self, server, llm_client):
        self.server = server
        self.llm_client = llm_client
    
    async def provide_hover(self, params):
        """Provide hover information"""
        if not self.llm_client:
            return None
        
        try:
            uri = params.text_document.uri
            position = params.position
            
            document_handler = getattr(self.server, '_document_handler', None)
            if not document_handler or uri not in document_handler.documents:
                return None
            
            text = document_handler.documents[uri]
            lines = text.split('\n')
            
            if position.line >= len(lines):
                return None
            
            current_line = lines[position.line]
            word = self._get_word_at_position(current_line, position.character)
            
            if not word:
                return None
            
            hover_info = await self._generate_ai_hover(text, word, position.line)
            
            if hover_info:
                return {
                    "contents": {"kind": "markdown", "value": hover_info},
                    "range": self._get_word_range(current_line, position.character, word)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Hover error: {e}")
            return None
    
    def _get_word_at_position(self, line: str, character: int) -> str:
        """Extract word at given position"""
        if character >= len(line):
            return ""
        
        # Find word boundaries
        start = character
        while start > 0 and (line[start-1].isalnum() or line[start-1] == '_'):
            start -= 1
        
        end = character
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1
        
        return line[start:end]
    
    def _get_word_range(self, line: str, character: int, word: str):
        """Get range for the word"""
        start_char = line.find(word, max(0, character - len(word)))
        if start_char == -1:
            start_char = character
        
        return {
            "start": {"line": 0, "character": start_char},
            "end": {"line": 0, "character": start_char + len(word)}
        }
    
    async def _generate_ai_hover(self, text: str, word: str, line: int) -> Optional[str]:
        """Generate AI-powered hover information"""
        try:
            context_lines = text.split('\n')[max(0, line-3):line+4]
            context = '\n'.join(context_lines)
            
            prompt = f"""
            Explain the symbol '{word}' in the following code context:
            
            {context}
            
            Provide a brief, helpful explanation in markdown format.
            """
            
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"AI hover generation error: {e}")
            return None

class CodeActionHandler:
    """Provides AI-powered code actions"""
    
    def __init__(self, server, llm_client):
        self.server = server
        self.llm_client = llm_client
    
    async def provide_code_actions(self, params):
        """Provide code actions"""
        if not self.llm_client:
            return []
        
        try:
            uri = params.text_document.uri
            range_param = params.range
            
            document_handler = getattr(self.server, '_document_handler', None)
            if not document_handler or uri not in document_handler.documents:
                return []
            
            text = document_handler.documents[uri]
            selected_text = self._extract_range_text(text, range_param)
            
            actions = []
            
            # Add refactoring actions
            if selected_text.strip():
                actions.extend([
                    {
                        "title": "🔧 Refactor with AI",
                        "kind": "refactor",
                        "command": {
                            "title": "Refactor Code",
                            "command": "maahelper.refactorCode",
                            "arguments": [uri, range_param]
                        }
                    },
                    {
                        "title": "📝 Explain Code",
                        "kind": "source",
                        "command": {
                            "title": "Explain Code",
                            "command": "maahelper.explainCode", 
                            "arguments": [uri, range_param]
                        }
                    },
                    {
                        "title": "🧪 Generate Tests",
                        "kind": "source",
                        "command": {
                            "title": "Generate Tests",
                            "command": "maahelper.generateTests",
                            "arguments": [uri, range_param]
                        }
                    }
                ])
            
            return actions
            
        except Exception as e:
            logger.error(f"Code action error: {e}")
            return []
    
    def _extract_range_text(self, text: str, range_param) -> str:
        """Extract text from range"""
        lines = text.split('\n')
        start_line = range_param.start.line
        end_line = range_param.end.line
        
        if start_line == end_line:
            if start_line < len(lines):
                line = lines[start_line]
                return line[range_param.start.character:range_param.end.character]
        else:
            selected_lines = []
            for i in range(start_line, min(end_line + 1, len(lines))):
                if i == start_line:
                    selected_lines.append(lines[i][range_param.start.character:])
                elif i == end_line:
                    selected_lines.append(lines[i][:range_param.end.character])
                else:
                    selected_lines.append(lines[i])
            return '\n'.join(selected_lines)
        
        return ""
