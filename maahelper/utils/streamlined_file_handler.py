"""
Streamlined File Handler with File Search
Optimized for directory structure display and file search with AI processing
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncIterator
import mimetypes
import json
import csv

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

console = Console()

class StreamlinedFileHandler:
    """Streamlined file handler focused on directory structure and file search"""
    
    SUPPORTED_EXTENSIONS = {
        # Code files
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.sql': 'sql',
        
        # Text files
        '.txt': 'text',
        '.md': 'markdown',
        '.rst': 'restructuredtext',
        '.log': 'log',
        
        # Data files
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.csv': 'csv',
        '.xml': 'xml',
        '.toml': 'toml',
        
        # Config files
        '.ini': 'ini',
        '.cfg': 'config',
        '.env': 'env',
        '.conf': 'config',
        
        # Documentation
        '.pdf': 'pdf',
        '.docx': 'docx',
        
        # Database
        '.sqlite': 'sqlite',
        '.db': 'database'
    }
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path).resolve()
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        
    def show_directory_structure(self, max_depth: int = 3, show_files: bool = False) -> str:
        """Show directory structure as a tree"""
        try:
            tree = Tree(f"📁 [bold blue]{self.workspace_path.name}[/bold blue]")
            
            def add_to_tree(current_path: Path, current_tree, depth: int):
                if depth >= max_depth:
                    return
                
                try:
                    # Get items and sort them
                    items = list(current_path.iterdir())
                    dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
                    files = [item for item in items if item.is_file() and item.suffix in self.SUPPORTED_EXTENSIONS]
                    
                    # Add directories first
                    for dir_path in sorted(dirs):
                        dir_branch = current_tree.add(f"📁 [cyan]{dir_path.name}[/cyan]")
                        add_to_tree(dir_path, dir_branch, depth + 1)
                    
                    # Add files if requested
                    if show_files:
                        for file_path in sorted(files):
                            file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix, 'unknown')
                            icon = self._get_file_icon(file_type)
                            current_tree.add(f"{icon} [green]{file_path.name}[/green] [dim]({file_type})[/dim]")
                            
                except PermissionError:
                    current_tree.add("[red]❌ Permission denied[/red]")
                except Exception as e:
                    current_tree.add(f"[red]❌ Error: {str(e)}[/red]")
            
            add_to_tree(self.workspace_path, tree, 0)
            
            console.print()
            console.print(tree)
            console.print()
            
            return "Directory structure displayed above."
            
        except Exception as e:
            error_msg = f"❌ Error showing directory structure: {e}"
            console.print(error_msg)
            return error_msg
    
    def _get_file_icon(self, file_type: str) -> str:
        """Get icon for file type"""
        icons = {
            'python': '🐍',
            'javascript': '🟨',
            'typescript': '🔷',
            'html': '🌐',
            'css': '🎨',
            'json': '📄',
            'yaml': '⚙️',
            'csv': '📊',
            'markdown': '📝',
            'text': '📄',
            'pdf': '📕',
            'docx': '📘',
            'database': '🗄️',
            'log': '📜'
        }
        return icons.get(file_type, '📄')
    
    async def file_search_command(self, filepath: str, llm_client) -> str:
        """Enhanced file-search command with AI processing"""
        try:
            file_path = Path(filepath)
            
            # Make path relative to workspace if needed
            if not file_path.is_absolute():
                file_path = self.workspace_path / file_path
            
            if not file_path.exists():
                return f"❌ File not found: {filepath}"
            
            if not file_path.is_file():
                return f"❌ Path is not a file: {filepath}"
            
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                return f"❌ File too large: {filepath} (max 50MB)"
            
            # Read and process file
            content = await self._read_file_content(file_path)
            if not content:
                return f"❌ Could not read file: {filepath}"
            
            # Show file info
            file_info = self._get_file_info(file_path)
            console.print(Panel.fit(
                f"[bold green]📁 File: {file_path.name}[/bold green]\n"
                f"[cyan]Type:[/cyan] {file_info['type']}\n"
                f"[cyan]Size:[/cyan] {file_info['size_human']}\n"
                f"[cyan]Lines:[/cyan] {file_info.get('lines', 'N/A')}\n"
                f"[cyan]Path:[/cyan] {file_path}",
                title="📄 File Information",
                border_style="green"
            ))
            
            # Process with AI for summary and analysis
            console.print("🤖 Analyzing file content...")
            
            analysis_prompt = f"""Analyze this file and provide:
1. Brief summary of what the file contains
2. Key functions/classes/components (if code)
3. Main purpose and functionality
4. Any issues or suggestions for improvement

File: {file_path.name}
Type: {file_info['type']}
Content:
{content[:4000]}{'...' if len(content) > 4000 else ''}"""
            
            # Use streaming for real-time response
            from ..utils.streaming import ModernStreamingHandler
            streaming_handler = ModernStreamingHandler(llm_client)
            analysis = await streaming_handler.stream_response(analysis_prompt, show_stats=False)
            
            return f"✅ File analysis completed for {file_path.name}"
            
        except Exception as e:
            error_msg = f"❌ Error in file-search: {e}"
            console.print(error_msg)
            return error_msg
    
    async def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with encoding detection"""
        try:
            # Try common encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, read as binary and decode safely
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode('utf-8', errors='replace')
                
        except Exception as e:
            console.print(f"❌ Error reading file {file_path}: {e}")
            return None
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            size = stat.st_size
            size_human = self._human_readable_size(size)
            
            file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower(), 'unknown')
            
            info = {
                'path': str(file_path),
                'name': file_path.name,
                'type': file_type,
                'size': size,
                'size_human': size_human,
                'extension': file_path.suffix.lower()
            }
            
            # For text files, count lines
            if file_type in ['python', 'javascript', 'typescript', 'text', 'markdown', 'css', 'html']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                    info['lines'] = lines
                except:
                    pass
            
            return info
            
        except Exception as e:
            return {
                'path': str(file_path),
                'name': file_path.name,
                'type': 'error',
                'size': 0,
                'size_human': '0 B',
                'error': str(e)
            }
    
    def _human_readable_size(self, size: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def list_supported_files(self, max_files: int = 50) -> List[Dict[str, Any]]:
        """List all supported files in workspace"""
        try:
            files = []
            
            def scan_directory(path: Path, depth: int = 0):
                if depth > 3:  # Limit depth
                    return
                
                try:
                    for item in path.iterdir():
                        if len(files) >= max_files:
                            break
                            
                        if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                            info = self._get_file_info(item)
                            info['relative_path'] = str(item.relative_to(self.workspace_path))
                            files.append(info)
                        
                        elif item.is_dir() and not item.name.startswith('.'):
                            scan_directory(item, depth + 1)
                            
                except PermissionError:
                    pass
                except Exception:
                    pass
            
            scan_directory(self.workspace_path)
            
            # Sort by type then name
            files.sort(key=lambda x: (x['type'], x['name']))
            
            return files
            
        except Exception as e:
            console.print(f"❌ Error listing files: {e}")
            return []
    
    def show_supported_files_table(self, max_files: int = 30):
        """Show supported files in a nice table"""
        files = self.list_supported_files(max_files)
        
        if not files:
            console.print("📁 No supported files found in workspace")
            return
        
        table = Table(
            title=f"📁 Supported Files in {self.workspace_path.name}",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("File", style="cyan", width=30)
        table.add_column("Type", style="green", width=15)
        table.add_column("Size", style="yellow", width=10)
        table.add_column("Path", style="dim", width=40)
        
        # Group by type for better organization
        by_type = {}
        for file_info in files:
            file_type = file_info['type']
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(file_info)
        
        for file_type in sorted(by_type.keys()):
            for file_info in by_type[file_type][:10]:  # Max 10 per type
                icon = self._get_file_icon(file_info['type'])
                table.add_row(
                    f"{icon} {file_info['name']}",
                    file_info['type'],
                    file_info['size_human'],
                    file_info['relative_path']
                )
        
        console.print()
        console.print(table)
        console.print()
        
        if len(files) > max_files:
            console.print(f"[dim]... and {len(files) - max_files} more files[/dim]")
        
        console.print(f"💡 Use [cyan]file-search <filepath>[/cyan] to analyze any file with AI")


# Global instance
file_handler = StreamlinedFileHandler()

# Backward compatibility
class EnhancedFileHandler(StreamlinedFileHandler):
    """Backward compatibility wrapper"""
    
    def read_file_content(self, filepath: str) -> Dict[str, Any]:
        """Legacy method for compatibility"""
        file_path = Path(filepath)
        if not file_path.is_absolute():
            file_path = self.workspace_path / file_path
        
        try:
            content = asyncio.run(self._read_file_content(file_path))
            info = self._get_file_info(file_path)
            
            return {
                'content': content,
                'file_info': info,
                'encoding': 'utf-8'
            }
        except Exception as e:
            return {
                'error': str(e),
                'content': None,
                'file_info': {'type': 'error'}
            }
    
    def get_file_suggestions(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Legacy method for compatibility"""
        self.workspace_path = Path(workspace_path)
        return self.list_supported_files()
