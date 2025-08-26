"""
MaaHelper Language Server Protocol Server
Main LSP server implementation for deep IDE integration
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

# Note: pygls is not installed by default, we'll implement a basic LSP server
# For production use, install: pip install pygls

try:
    from pygls.server import LanguageServer
    from lsprotocol.types import (
        InitializeParams,
        InitializeResult,
        ServerCapabilities,
        TextDocumentSyncKind,
        CompletionOptions,
        HoverOptions,
        CodeActionOptions,
        DiagnosticOptions,
        WorkspaceFolder
    )
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False
    # Fallback basic implementation
    class LanguageServer:
        def __init__(self, name, version):
            self.name = name
            self.version = version

        def feature(self, method):
            def decorator(func):
                return func
            return decorator

        def start_io(self):
            print("LSP Server would start here (pygls not installed)")

        def start_tcp(self, host, port):
            print(f"LSP Server would start on {host}:{port} (pygls not installed)")

    # Fallback type definitions for when pygls is not available
    class InitializeParams:
        def __init__(self):
            self.workspace_folders = None
            self.root_uri = None

    class InitializeResult:
        def __init__(self, capabilities=None):
            self.capabilities = capabilities

    class ServerCapabilities:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class TextDocumentSyncKind:
        Incremental = 2

    class CompletionOptions:
        def __init__(self, trigger_characters=None, resolve_provider=False):
            self.trigger_characters = trigger_characters or []
            self.resolve_provider = resolve_provider

    class HoverOptions:
        def __init__(self):
            pass

    class CodeActionOptions:
        def __init__(self, code_action_kinds=None):
            self.code_action_kinds = code_action_kinds or []

    class DiagnosticOptions:
        def __init__(self, inter_file_dependencies=False, workspace_diagnostics=False):
            self.inter_file_dependencies = inter_file_dependencies
            self.workspace_diagnostics = workspace_diagnostics

    class WorkspaceFolder:
        def __init__(self, uri=None, name=None):
            self.uri = uri
            self.name = name

from ..core.llm_client import UnifiedLLMClient, create_llm_client
from ..managers.streamlined_api_key_manager import api_key_manager
from .handlers import (
    TextDocumentHandler,
    CompletionHandler,
    DiagnosticsHandler,
    HoverHandler,
    CodeActionHandler
)

logger = logging.getLogger(__name__)

class MaaHelperLSPServer:
    """Main Language Server Protocol server for MaaHelper"""

    def __init__(self):
        self.server = LanguageServer('maahelper-lsp', 'v0.1.0')
        self.llm_client: Optional[UnifiedLLMClient] = None
        self.workspace_folders: List[WorkspaceFolder] = []
        self.document_handler: Optional[TextDocumentHandler] = None
        self.completion_handler: Optional[CompletionHandler] = None
        self.diagnostics_handler: Optional[DiagnosticsHandler] = None
        self.hover_handler: Optional[HoverHandler] = None
        self.code_action_handler: Optional[CodeActionHandler] = None

        # Only setup handlers if pygls is available
        if PYGLS_AVAILABLE:
            self._setup_handlers()
        else:
            logger.warning("pygls not available. LSP server will have limited functionality.")
    
    def _setup_handlers(self):
        """Setup LSP message handlers"""
        
        @self.server.feature('initialize')
        async def initialize(params: InitializeParams) -> InitializeResult:
            """Initialize the language server"""
            logger.info("Initializing MaaHelper LSP Server")
            
            # Store workspace folders
            if params.workspace_folders:
                self.workspace_folders = params.workspace_folders
            elif params.root_uri:
                self.workspace_folders = [WorkspaceFolder(
                    uri=params.root_uri,
                    name=Path(params.root_uri).name
                )]
            
            # Initialize LLM client
            await self._initialize_llm_client()
            
            # Initialize handlers
            self._initialize_handlers()
            
            return InitializeResult(
                capabilities=ServerCapabilities(
                    text_document_sync=TextDocumentSyncKind.Incremental,
                    completion_provider=CompletionOptions(
                        trigger_characters=['.', '(', '[', '"', "'"],
                        resolve_provider=True
                    ),
                    hover_provider=HoverOptions(),
                    code_action_provider=CodeActionOptions(
                        code_action_kinds=['quickfix', 'refactor', 'source']
                    ),
                    diagnostic_provider=DiagnosticOptions(
                        inter_file_dependencies=True,
                        workspace_diagnostics=True
                    )
                )
            )
        
        @self.server.feature('initialized')
        async def initialized(params):
            """Server initialized notification"""
            logger.info("MaaHelper LSP Server initialized successfully")
            
            # Start background tasks
            if self.diagnostics_handler:
                asyncio.create_task(self.diagnostics_handler.start_background_analysis())
        
        @self.server.feature('shutdown')
        async def shutdown(params):
            """Shutdown the server"""
            logger.info("Shutting down MaaHelper LSP Server")
            
            # Cleanup handlers
            if self.diagnostics_handler:
                await self.diagnostics_handler.stop_background_analysis()
        
        @self.server.feature('textDocument/didOpen')
        async def did_open(params):
            """Handle document open"""
            if self.document_handler:
                await self.document_handler.did_open(params)
        
        @self.server.feature('textDocument/didChange')
        async def did_change(params):
            """Handle document change"""
            if self.document_handler:
                await self.document_handler.did_change(params)
        
        @self.server.feature('textDocument/didSave')
        async def did_save(params):
            """Handle document save"""
            if self.document_handler:
                await self.document_handler.did_save(params)
            
            # Trigger diagnostics on save
            if self.diagnostics_handler:
                await self.diagnostics_handler.analyze_document(params.text_document.uri)
        
        @self.server.feature('textDocument/didClose')
        async def did_close(params):
            """Handle document close"""
            if self.document_handler:
                await self.document_handler.did_close(params)
        
        @self.server.feature('textDocument/completion')
        async def completion(params):
            """Handle completion requests"""
            if self.completion_handler:
                return await self.completion_handler.provide_completion(params)
            return None
        
        @self.server.feature('textDocument/hover')
        async def hover(params):
            """Handle hover requests"""
            if self.hover_handler:
                return await self.hover_handler.provide_hover(params)
            return None
        
        @self.server.feature('textDocument/codeAction')
        async def code_action(params):
            """Handle code action requests"""
            if self.code_action_handler:
                return await self.code_action_handler.provide_code_actions(params)
            return []
        
        @self.server.feature('textDocument/diagnostic')
        async def diagnostic(params):
            """Handle diagnostic requests"""
            if self.diagnostics_handler:
                return await self.diagnostics_handler.provide_diagnostics(params)
            return []
    
    async def _initialize_llm_client(self):
        """Initialize the LLM client for AI operations"""
        try:
            # Get available providers
            providers = api_key_manager.get_available_providers()
            if not providers:
                logger.warning("No API keys configured. LSP will have limited functionality.")
                return
            
            # Use the first available provider
            provider = providers[0]
            self.llm_client = await create_llm_client(provider)
            logger.info(f"LLM client initialized with provider: {provider}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
    
    def _initialize_handlers(self):
        """Initialize all LSP handlers"""
        self.document_handler = TextDocumentHandler(self.server)
        self.completion_handler = CompletionHandler(self.server, self.llm_client)
        self.diagnostics_handler = DiagnosticsHandler(self.server, self.llm_client)
        self.hover_handler = HoverHandler(self.server, self.llm_client)
        self.code_action_handler = CodeActionHandler(self.server, self.llm_client)
    
    def start_server(self, port: int = 2087):
        """Start the LSP server"""
        if not PYGLS_AVAILABLE:
            logger.warning("pygls not installed. Cannot start LSP server.")
            print("❌ LSP Server cannot start: pygls not installed")
            print("💡 Install pygls with: pip install pygls")
            return

        logger.info(f"Starting MaaHelper LSP Server on port {port}")
        self.server.start_tcp('localhost', port)

    def start_stdio(self):
        """Start the LSP server using stdio"""
        if not PYGLS_AVAILABLE:
            logger.warning("pygls not installed. Cannot start LSP server.")
            print("❌ LSP Server cannot start: pygls not installed")
            print("💡 Install pygls with: pip install pygls")
            return

        logger.info("Starting MaaHelper LSP Server with stdio")
        self.server.start_io()

def main():
    """Main entry point for the LSP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MaaHelper Language Server')
    parser.add_argument('--port', type=int, help='TCP port to listen on')
    parser.add_argument('--stdio', action='store_true', help='Use stdio for communication')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check if pygls is available
    if not PYGLS_AVAILABLE:
        print("❌ Cannot start LSP server: pygls not installed")
        print("💡 Install pygls with: pip install pygls")
        sys.exit(1)

    # Create and start server
    server = MaaHelperLSPServer()

    try:
        if args.stdio:
            server.start_stdio()
        elif args.port:
            server.start_server(args.port)
        else:
            # Default to stdio
            server.start_stdio()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
