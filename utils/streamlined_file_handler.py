# """
# Streamlined File Handler with File Search
# Optimized for directory structure display and file search with AI processing
# """
# from datetime import datetime  # Ensure this is imported at the top
# import os
# import asyncio
# from pathlib import Path
# from typing import Dict, List, Optional, Any, AsyncIterator
# import mimetypes
# import json
# import csv

# from rich.console import Console
# from rich.table import Table
# from rich.panel import Panel
# from rich.tree import Tree
# from rich.text import Text

# console = Console()

# class StreamlinedFileHandler:
#     """Streamlined file handler focused on directory structure and file search"""
    
#     SUPPORTED_EXTENSIONS = {
#         # Code files
#         '.py': 'python',
#         '.js': 'javascript',
#         '.ts': 'typescript',
#         '.jsx': 'javascript',
#         '.tsx': 'typescript',
#         '.html': 'html',
#         '.css': 'css',
#         '.java': 'java',
#         '.cpp': 'cpp',
#         '.c': 'c',
#         '.cs': 'csharp',
#         '.php': 'php',
#         '.rb': 'ruby',
#         '.go': 'go',
#         '.rs': 'rust',
#         '.sql': 'sql',
        
#         # Text files
#         '.txt': 'text',
#         '.md': 'markdown',
#         '.rst': 'restructuredtext',
#         '.log': 'log',
        
#         # Data files
#         '.json': 'json',
#         '.yaml': 'yaml',
#         '.yml': 'yaml',
#         '.csv': 'csv',
#         '.xml': 'xml',
#         '.toml': 'toml',
        
#         # Config files
#         '.ini': 'ini',
#         '.cfg': 'config',
#         '.env': 'env',
#         '.conf': 'config',
        
#         # Documentation
#         '.pdf': 'pdf',
#         '.docx': 'docx',
        
#         # Database
#         '.sqlite': 'sqlite',
#         '.db': 'database'
#     }
    
#     def __init__(self, workspace_path: str = "."):
#         self.workspace_path = Path(workspace_path).resolve()
#         self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        
#     def show_directory_structure(self, max_depth: int = 3, show_files: bool = False) -> str:
#         """Show directory structure as a tree"""
#         try:
#             tree = Tree(f"📁 [bold blue]{self.workspace_path.name}[/bold blue]")
            
#             def add_to_tree(current_path: Path, current_tree, depth: int):
#                 if depth >= max_depth:
#                     return
                
#                 try:
#                     # Get items and sort them
#                     items = list(current_path.iterdir())
#                     dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
#                     files = [item for item in items if item.is_file() and item.suffix in self.SUPPORTED_EXTENSIONS]
                    
#                     # Add directories first
#                     for dir_path in sorted(dirs):
#                         dir_branch = current_tree.add(f"📁 [cyan]{dir_path.name}[/cyan]")
#                         add_to_tree(dir_path, dir_branch, depth + 1)
                    
#                     # Add files if requested
#                     if show_files:
#                         for file_path in sorted(files):
#                             file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix, 'unknown')
#                             icon = self._get_file_icon(file_type)
#                             current_tree.add(f"{icon} [green]{file_path.name}[/green] [dim]({file_type})[/dim]")
                            
#                 except PermissionError:
#                     current_tree.add("[red]❌ Permission denied[/red]")
#                 except Exception as e:
#                     current_tree.add(f"[red]❌ Error: {str(e)}[/red]")
            
#             add_to_tree(self.workspace_path, tree, 0)
            
#             console.print()
#             console.print(tree)
#             console.print()
            
#             return "Directory structure displayed above."
            
#         except Exception as e:
#             error_msg = f"❌ Error showing directory structure: {e}"
#             console.print(error_msg)
#             return error_msg
    
#     def _get_file_icon(self, file_type: str) -> str:
#         """Get icon for file type"""
#         icons = {
#             'python': '🐍',
#             'javascript': '🟨',
#             'typescript': '🔷',
#             'html': '🌐',
#             'css': '🎨',
#             'json': '📄',
#             'yaml': '⚙️',
#             'csv': '📊',
#             'markdown': '📝',
#             'text': '📄',
#             'pdf': '📕',
#             'docx': '📘',
#             'database': '🗄️',
#             'log': '📜'
#         }
#         return icons.get(file_type, '📄')
    
#     async def file_search_command(self, filepath: str, llm_client) -> str:
#         """Enhanced file-search command with AI processing"""
#         try:
#             file_path = Path(filepath)
            
#             # Make path relative to workspace if needed
#             if not file_path.is_absolute():
#                 file_path = self.workspace_path / file_path
            
#             if not file_path.exists():
#                 return f"❌ File not found: {filepath}"
            
#             if not file_path.is_file():
#                 return f"❌ Path is not a file: {filepath}"
            
#             # Check file size
#             if file_path.stat().st_size > self.max_file_size:
#                 return f"❌ File too large: {filepath} (max 50MB)"
            
#             # Read and process file
#             content = await self._read_file_content(file_path)
#             if not content:
#                 return f"❌ Could not read file: {filepath}"
            
#             # Show file info
#             file_info = self._get_file_info(file_path)
#             stat = file_path.stat()
#             console.print(Panel.fit(
#     f"[bold green]📁 File: {file_path.name}[/bold green]\n"
#     f"[cyan]Type:[/cyan] {file_info['type']}\n"
#     f"[cyan]Size:[/cyan] {file_info['size_human']} ({file_info['size']} bytes)\n"
#     f"[cyan]Lines:[/cyan] {file_info.get('lines', 'N/A')}\n"
#     f"[cyan]Path:[/cyan] {file_path}\n"
#     f"[cyan]Created:[/cyan] {datetime.fromtimestamp(stat.st_ctime)}\n"
#     f"[cyan]Modified:[/cyan] {datetime.fromtimestamp(stat.st_mtime)}",
#     title="📄 File Information",
#     border_style="green"
# ))
#             # console.print(Panel.fit(
#             #     f"[bold green]📁 File: {file_path.name}[/bold green]\n"
#             #     f"[cyan]Type:[/cyan] {file_info['type']}\n"
#             #     f"[cyan]Size:[/cyan] {file_info['size_human']}\n"
#             #     f"[cyan]Lines:[/cyan] {file_info.get('lines', 'N/A')}\n"
#             #     f"[cyan]Path:[/cyan] {file_path}",
#             #     title="📄 File Information",
#             #     border_style="green"
#             # ))

            
            
#             # Process with AI for summary and analysis
#             console.print("🤖 Analyzing file content...")
            
#             analysis_prompt = f"""Analyze this file and provide:
# 1. Brief summary of what the file contains
# 2. Key functions/classes/components (if code)
# 3. Main purpose and functionality
# 4. Any issues or suggestions for improvement

# File: {file_path.name}
# Type: {file_info['type']}
# Content:
# {content[:4000]}{'...' if len(content) > 4000 else ''}"""
            
#             # Use streaming for real-time response
#             from ..utils.streaming import ModernStreamingHandler
#             streaming_handler = ModernStreamingHandler(llm_client)
#             analysis = await streaming_handler.stream_response(analysis_prompt, show_stats=False)
            
#             return f"✅ File analysis completed for {file_path.name}"
            
#         except Exception as e:
#             error_msg = f"❌ Error in file-search: {e}"
#             console.print(error_msg)
#             return error_msg
    
#     async def _read_file_content(self, file_path: Path) -> Optional[str]:
#         """Read file content with encoding detection"""
#         try:
#             # Try common encodings
#             encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
            
#             for encoding in encodings:
#                 try:
#                     with open(file_path, 'r', encoding=encoding) as f:
#                         return f.read()
#                 except UnicodeDecodeError:
#                     continue
            
#             # If all encodings fail, read as binary and decode safely
#             with open(file_path, 'rb') as f:
#                 content = f.read()
#                 return content.decode('utf-8', errors='replace')
                
#         except Exception as e:
#             console.print(f"❌ Error reading file {file_path}: {e}")
#             return None
    
#     def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
#         """Get comprehensive file information"""
#         try:
#             stat = file_path.stat()
#             size = stat.st_size
#             size_human = self._human_readable_size(size)
            
#             file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower(), 'unknown')
            
#             info = {
#                 'path': str(file_path),
#                 'name': file_path.name,
#                 'type': file_type,
#                 'size': size,
#                 'size_human': size_human,
#                 'extension': file_path.suffix.lower()
#             }
            
#             # For text files, count lines
#             if file_type in ['python', 'javascript', 'typescript', 'text', 'markdown', 'css', 'html']:
#                 try:
#                     with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                         lines = sum(1 for _ in f)
#                     info['lines'] = lines
#                 except:
#                     pass
            
#             return info
            
#         except Exception as e:
#             return {
#                 'path': str(file_path),
#                 'name': file_path.name,
#                 'type': 'error',
#                 'size': 0,
#                 'size_human': '0 B',
#                 'error': str(e)
#             }
    
#     def _human_readable_size(self, size: int) -> str:
#         """Convert bytes to human readable format"""
#         for unit in ['B', 'KB', 'MB', 'GB']:
#             if size < 1024.0:
#                 return f"{size:.1f} {unit}"
#             size /= 1024.0
#         return f"{size:.1f} TB"
    
#     def list_supported_files(self, max_files: int = 50) -> List[Dict[str, Any]]:
#         """List all supported files in workspace"""
#         try:
#             files = []
            
#             def scan_directory(path: Path, depth: int = 0):
#                 if depth > 3:  # Limit depth
#                     return
                
#                 try:
#                     for item in path.iterdir():
#                         if len(files) >= max_files:
#                             break
                            
#                         if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
#                             info = self._get_file_info(item)
#                             info['relative_path'] = str(item.relative_to(self.workspace_path))
#                             files.append(info)
                        
#                         elif item.is_dir() and not item.name.startswith('.'):
#                             scan_directory(item, depth + 1)
                            
#                 except PermissionError:
#                     pass
#                 except Exception:
#                     pass
            
#             scan_directory(self.workspace_path)
            
#             # Sort by type then name
#             files.sort(key=lambda x: (x['type'], x['name']))
            
#             return files
            
#         except Exception as e:
#             console.print(f"❌ Error listing files: {e}")
#             return []
    
#     def show_supported_files_table(self, max_files: int = 30):
#         """Show supported files in a nice table"""
#         files = self.list_supported_files(max_files)
        
#         if not files:
#             console.print("📁 No supported files found in workspace")
#             return
        
#         table = Table(
#             title=f"📁 Supported Files in {self.workspace_path.name}",
#             show_header=True,
#             header_style="bold magenta"
#         )
        
#         table.add_column("File", style="cyan", width=30)
#         table.add_column("Type", style="green", width=15)
#         table.add_column("Size", style="yellow", width=10)
#         table.add_column("Path", style="dim", width=40)
        
#         # Group by type for better organization
#         by_type = {}
#         for file_info in files:
#             file_type = file_info['type']
#             if file_type not in by_type:
#                 by_type[file_type] = []
#             by_type[file_type].append(file_info)
        
#         for file_type in sorted(by_type.keys()):
#             for file_info in by_type[file_type][:10]:  # Max 10 per type
#                 icon = self._get_file_icon(file_info['type'])
#                 table.add_row(
#                     f"{icon} {file_info['name']}",
#                     file_info['type'],
#                     file_info['size_human'],
#                     file_info['relative_path']
#                 )
        
#         console.print()
#         console.print(table)
#         console.print()
        
#         if len(files) > max_files:
#             console.print(f"[dim]... and {len(files) - max_files} more files[/dim]")
        
#         console.print(f"💡 Use [cyan]file-search <filepath>[/cyan] to analyze any file with AI")


# # Global instance
# file_handler = StreamlinedFileHandler()

# # Backward compatibility
# class EnhancedFileHandler(StreamlinedFileHandler):
#     """Backward compatibility wrapper"""
    
#     def read_file_content(self, filepath: str) -> Dict[str, Any]:
#         """Legacy method for compatibility"""
#         file_path = Path(filepath)
#         if not file_path.is_absolute():
#             file_path = self.workspace_path / file_path
        
#         try:
#             content = asyncio.run(self._read_file_content(file_path))
#             info = self._get_file_info(file_path)
            
#             return {
#                 'content': content,
#                 'file_info': info,
#                 'encoding': 'utf-8'
#             }
#         except Exception as e:
#             return {
#                 'error': str(e),
#                 'content': None,
#                 'file_info': {'type': 'error'}
#             }
    
#     def get_file_suggestions(self, workspace_path: str) -> List[Dict[str, Any]]:
#         """Legacy method for compatibility"""
#         self.workspace_path = Path(workspace_path)
#         return self.list_supported_files()


# """
# Streamlined File Handler with File Search
# Optimized for directory structure display and file search with AI processing
# """
# from datetime import datetime  # Ensure this is imported at the top
# import os
# import asyncio
# from pathlib import Path
# from typing import Dict, List, Optional, Any, AsyncIterator
# import mimetypes
# import json
# import csv

# from rich.console import Console
# from rich.table import Table
# from rich.panel import Panel
# from rich.tree import Tree
# from rich.text import Text

# console = Console()

# class StreamlinedFileHandler:
#     """Streamlined file handler focused on directory structure and file search"""
    
#     SUPPORTED_EXTENSIONS = {
#         # Code files
#         '.py': 'python',
#         '.js': 'javascript',
#         '.ts': 'typescript',
#         '.jsx': 'javascript',
#         '.tsx': 'typescript',
#         '.html': 'html',
#         '.css': 'css',
#         '.java': 'java',
#         '.cpp': 'cpp',
#         '.c': 'c',
#         '.cs': 'csharp',
#         '.php': 'php',
#         '.rb': 'ruby',
#         '.go': 'go',
#         '.rs': 'rust',
#         '.sql': 'sql',
        
#         # Text files
#         '.txt': 'text',
#         '.md': 'markdown',
#         '.rst': 'restructuredtext',
#         '.log': 'log',
        
#         # Data files
#         '.json': 'json',
#         '.yaml': 'yaml',
#         '.yml': 'yaml',
#         '.csv': 'csv',
#         '.xml': 'xml',
#         '.toml': 'toml',
        
#         # Config files
#         '.ini': 'ini',
#         '.cfg': 'config',
#         '.env': 'env',
#         '.conf': 'config',
        
#         # Documentation
#         '.pdf': 'pdf',
#         '.docx': 'docx',
        
#         # Database
#         '.sqlite': 'sqlite',
#         '.db': 'database'
#     }
    
#     def __init__(self, workspace_path: str = "."):
#         self.workspace_path = Path(workspace_path).resolve()
#         self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        
#     def show_directory_structure(self, max_depth: int = 3, show_files: bool = False) -> str:
#         """Show directory structure as a tree"""
#         try:
#             tree = Tree(f"📁 [bold blue]{self.workspace_path.name}[/bold blue]")
            
#             def add_to_tree(current_path: Path, current_tree, depth: int):
#                 if depth >= max_depth:
#                     return
                
#                 try:
#                     # Get items and sort them
#                     items = list(current_path.iterdir())
#                     dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
#                     files = [item for item in items if item.is_file() and item.suffix in self.SUPPORTED_EXTENSIONS]
                    
#                     # Add directories first
#                     for dir_path in sorted(dirs):
#                         dir_branch = current_tree.add(f"📁 [cyan]{dir_path.name}[/cyan]")
#                         add_to_tree(dir_path, dir_branch, depth + 1)
                    
#                     # Add files if requested
#                     if show_files:
#                         for file_path in sorted(files):
#                             file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix, 'unknown')
#                             icon = self._get_file_icon(file_type)
#                             current_tree.add(f"{icon} [green]{file_path.name}[/green] [dim]({file_type})[/dim]")
                            
#                 except PermissionError:
#                     current_tree.add("[red]❌ Permission denied[/red]")
#                 except Exception as e:
#                     current_tree.add(f"[red]❌ Error: {str(e)}[/red]")
            
#             add_to_tree(self.workspace_path, tree, 0)
            
#             console.print()
#             console.print(tree)
#             console.print()
            
#             return "Directory structure displayed above."
            
#         except Exception as e:
#             error_msg = f"❌ Error showing directory structure: {e}"
#             console.print(error_msg)
#             return error_msg
    
#     def _get_file_icon(self, file_type: str) -> str:
#         """Get icon for file type"""
#         icons = {
#             'python': '🐍',
#             'javascript': '🟨',
#             'typescript': '🔷',
#             'html': '🌐',
#             'css': '🎨',
#             'json': '📄',
#             'yaml': '⚙️',
#             'csv': '📊',
#             'markdown': '📝',
#             'text': '📄',
#             'pdf': '📕',
#             'docx': '📘',
#             'database': '🗄️',
#             'log': '📜'
#         }
#         return icons.get(file_type, '📄')
    
#     async def file_search_command(self, filepath: str, llm_client) -> str:
#         """Enhanced file-search command with AI processing"""
#         try:
#             file_path = Path(filepath)
            
#             # Make path relative to workspace if needed
#             if not file_path.is_absolute():
#                 file_path = self.workspace_path / file_path
            
#             if not file_path.exists():
#                 return f"❌ File not found: {filepath}"
            
#             if not file_path.is_file():
#                 return f"❌ Path is not a file: {filepath}"
            
#             # Check file size
#             if file_path.stat().st_size > self.max_file_size:
#                 return f"❌ File too large: {filepath} (max 50MB)"
            
#             # Read and process file
#             content = await self._read_file_content(file_path)
#             if not content:
#                 return f"❌ Could not read file: {filepath}"
            
#             # Show file info
#             file_info = self._get_file_info(file_path)
#             stat = file_path.stat()
#             console.print(Panel.fit(
#                 f"[bold green]📁 File: {file_path.name}[/bold green]\n"
#                 f"[cyan]Type:[/cyan] {file_info['type']}\n"
#                 f"[cyan]Size:[/cyan] {file_info['size_human']} ({file_info['size']} bytes)\n"
#                 f"[cyan]Lines:[/cyan] {file_info.get('lines', 'N/A')}\n"
#                 f"[cyan]Path:[/cyan] {file_path}\n"
#                 f"[cyan]Created:[/cyan] {datetime.fromtimestamp(stat.st_ctime)}\n"
#                 f"[cyan]Modified:[/cyan] {datetime.fromtimestamp(stat.st_mtime)}",
#                 title="📄 File Information",
#                 border_style="green"
#             ))
            
#             # Process with AI for summary and analysis
#             console.print("🤖 Analyzing file content...")
            
#             analysis_prompt = f"""Analyze this file and provide:
# 1. Brief summary of what the file contains
# 2. Key functions/classes/components (if code)
# 3. Main purpose and functionality
# 4. Any issues or suggestions for improvement

# File: {file_path.name}
# Type: {file_info['type']}
# Content:
# {content[:4000]}{'...' if len(content) > 4000 else ''}"""
            
#             # Simple mock analysis for testing (replace with actual LLM call)
#             console.print("🔍 [bold cyan]AI Analysis:[/bold cyan]")
            
#             if hasattr(llm_client, 'stream_completion'):
#                 # If it's a real LLM client, use it
#                 async for chunk in llm_client.stream_completion(analysis_prompt):
#                     print(chunk, end='', flush=True)
#                 print()  # New line after streaming
#             else:
#                 # Mock analysis for testing
#                 mock_analysis = f"""
# 📋 **File Analysis Summary**

# **File:** {file_path.name}
# **Type:** {file_info['type']}
# **Size:** {file_info['size_human']}

# **Content Summary:**
# This appears to be a {file_info['type']} file containing {file_info.get('lines', 'unknown')} lines.

# **Key Components:**
# - File structure and content analysis
# - Error handling and validation
# - File type detection and processing

# **Main Purpose:**
# The file serves as a data/configuration/code file within the project structure.

# **Suggestions:**
# - Content appears well-structured
# - Consider adding documentation if missing
# - Ensure proper error handling where applicable
# """
#                 console.print(Panel(mock_analysis, title="🤖 AI Analysis", border_style="blue"))
            
#             return f"✅ File analysis completed for {file_path.name}"
            
#         except Exception as e:
#             error_msg = f"❌ Error in file-search: {e}"
#             console.print(error_msg)
#             return error_msg
    
#     async def _read_file_content(self, file_path: Path) -> Optional[str]:
#         """Read file content with encoding detection"""
#         try:
#             # Try common encodings
#             encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
            
#             for encoding in encodings:
#                 try:
#                     with open(file_path, 'r', encoding=encoding) as f:
#                         return f.read()
#                 except UnicodeDecodeError:
#                     continue
            
#             # If all encodings fail, read as binary and decode safely
#             with open(file_path, 'rb') as f:
#                 content = f.read()
#                 return content.decode('utf-8', errors='replace')
                
#         except Exception as e:
#             console.print(f"❌ Error reading file {file_path}: {e}")
#             return None
    
#     def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
#         """Get comprehensive file information"""
#         try:
#             stat = file_path.stat()
#             size = stat.st_size
#             size_human = self._human_readable_size(size)
            
#             file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower(), 'unknown')
            
#             info = {
#                 'path': str(file_path),
#                 'name': file_path.name,
#                 'type': file_type,
#                 'size': size,
#                 'size_human': size_human,
#                 'extension': file_path.suffix.lower()
#             }
            
#             # For text files, count lines
#             if file_type in ['python', 'javascript', 'typescript', 'text', 'markdown', 'css', 'html']:
#                 try:
#                     with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
#                         lines = sum(1 for _ in f)
#                     info['lines'] = lines
#                 except:
#                     pass
            
#             return info
            
#         except Exception as e:
#             return {
#                 'path': str(file_path),
#                 'name': file_path.name,
#                 'type': 'error',
#                 'size': 0,
#                 'size_human': '0 B',
#                 'error': str(e)
#             }
    
#     def _human_readable_size(self, size: int) -> str:
#         """Convert bytes to human readable format"""
#         for unit in ['B', 'KB', 'MB', 'GB']:
#             if size < 1024.0:
#                 return f"{size:.1f} {unit}"
#             size /= 1024.0
#         return f"{size:.1f} TB"
    
#     def list_supported_files(self, max_files: int = 50) -> List[Dict[str, Any]]:
#         """List all supported files in workspace"""
#         try:
#             files = []
            
#             def scan_directory(path: Path, depth: int = 0):
#                 if depth > 3:  # Limit depth
#                     return
                
#                 try:
#                     for item in path.iterdir():
#                         if len(files) >= max_files:
#                             break
                            
#                         if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
#                             info = self._get_file_info(item)
#                             info['relative_path'] = str(item.relative_to(self.workspace_path))
#                             files.append(info)
                        
#                         elif item.is_dir() and not item.name.startswith('.'):
#                             scan_directory(item, depth + 1)
                            
#                 except PermissionError:
#                     pass
#                 except Exception:
#                     pass
            
#             scan_directory(self.workspace_path)
            
#             # Sort by type then name
#             files.sort(key=lambda x: (x['type'], x['name']))
            
#             return files
            
#         except Exception as e:
#             console.print(f"❌ Error listing files: {e}")
#             return []
    
#     def show_supported_files_table(self, max_files: int = 30):
#         """Show supported files in a nice table"""
#         files = self.list_supported_files(max_files)
        
#         if not files:
#             console.print("📁 No supported files found in workspace")
#             return
        
#         table = Table(
#             title=f"📁 Supported Files in {self.workspace_path.name}",
#             show_header=True,
#             header_style="bold magenta"
#         )
        
#         table.add_column("File", style="cyan", width=30)
#         table.add_column("Type", style="green", width=15)
#         table.add_column("Size", style="yellow", width=10)
#         table.add_column("Path", style="dim", width=40)
        
#         # Group by type for better organization
#         by_type = {}
#         for file_info in files:
#             file_type = file_info['type']
#             if file_type not in by_type:
#                 by_type[file_type] = []
#             by_type[file_type].append(file_info)
        
#         for file_type in sorted(by_type.keys()):
#             for file_info in by_type[file_type][:10]:  # Max 10 per type
#                 icon = self._get_file_icon(file_info['type'])
#                 table.add_row(
#                     f"{icon} {file_info['name']}",
#                     file_info['type'],
#                     file_info['size_human'],
#                     file_info['relative_path']
#                 )
        
#         console.print()
#         console.print(table)
#         console.print()
        
#         if len(files) > max_files:
#             console.print(f"[dim]... and {len(files) - max_files} more files[/dim]")
        
#         console.print(f"💡 Use [cyan]file-search <filepath>[/cyan] to analyze any file with AI")


# # Global instance
# file_handler = StreamlinedFileHandler()

# # Backward compatibility
# class EnhancedFileHandler(StreamlinedFileHandler):
#     """Backward compatibility wrapper"""
    
#     def read_file_content(self, filepath: str) -> Dict[str, Any]:
#         """Legacy method for compatibility"""
#         file_path = Path(filepath)
#         if not file_path.is_absolute():
#             file_path = self.workspace_path / file_path
        
#         try:
#             content = asyncio.run(self._read_file_content(file_path))
#             info = self._get_file_info(file_path)
            
#             return {
#                 'content': content,
#                 'file_info': info,
#                 'encoding': 'utf-8'
#             }
#         except Exception as e:
#             return {
#                 'error': str(e),
#                 'content': None,
#                 'file_info': {'type': 'error'}
#             }
    
#     def get_file_suggestions(self, workspace_path: str) -> List[Dict[str, Any]]:
#         """Legacy method for compatibility"""
#         self.workspace_path = Path(workspace_path)
#         return self.list_supported_files()

#!/usr/bin/env python3
"""
Streamlined File Handler with File Search
Optimized for directory structure display and file search with AI processing
"""
from datetime import datetime  # Ensure this is imported at the top
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
            
            # Read and process file - ACTUAL IMPLEMENTATION
            content = await self._read_file_content(file_path)
            if not content:
                return f"❌ Could not read file: {filepath}"
            
            # Show file info
            file_info = self._get_file_info(file_path)
            stat = file_path.stat()

            console.print(Panel.fit(
                f"[bold green]📁 File: {file_path.name}[/bold green]\n"
                f"[cyan]Type:[/cyan] {file_info['type']}\n"
                f"[cyan]Size:[/cyan] {file_info['size_human']} ({file_info['size']} bytes)\n"
                f"[cyan]Lines:[/cyan] {file_info.get('lines', 'N/A')}\n"
                f"[cyan]Path:[/cyan] {file_path}\n"
                f"[cyan]Created:[/cyan] {datetime.fromtimestamp(stat.st_ctime)}\n"
                f"[cyan]Modified:[/cyan] {datetime.fromtimestamp(stat.st_mtime)}",
                title="📄 File Information",
                border_style="green"
            ))
            
            console.print("\n📄 [bold cyan]File Content:[/bold cyan]")
            content_lines = content.split('\n')
            display_content = content if len(content) <= 3000 else content[:3000]
            content_note = "" if len(content) <= 3000 else f"\n\n[dim]... (showing first 3000 characters of {len(content)} total)[/dim]"

            console.print(Panel(
                display_content + content_note,
                title=f"📝 Content of {file_path.name}",
                border_style="blue",
                expand=False
            ))
            
            
            # ========== REAL CONTENT ANALYSIS ==========
            console.print("\n🤖 [bold cyan]Analyzing file content...[/bold cyan]")
            
            # Prepare analysis prompt with ACTUAL content
            analysis_prompt = f"""Analyze this file and provide:
1. Brief summary of what the file contains
2. Key functions/classes/components (if code)
3. Main purpose and functionality
4. Any issues or suggestions for improvement

File: {file_path.name}
Type: {file_info['type']}
Size: {file_info['size_human']}
Lines: {file_info.get('lines', 'N/A')}

Content:
{content}
"""
            
            # Generate analysis based on ACTUAL content
            analysis_result = await self._generate_content_analysis(content, file_info, file_path)
            
            # Check if we have a real LLM client
            if hasattr(llm_client, 'stream_completion'):
                console.print("🔍 [bold cyan]AI Analysis:[/bold cyan]")
                try:
                    # Use streaming for real-time response
                    from ..utils.streaming import ModernStreamingHandler
                    streaming_handler = ModernStreamingHandler(llm_client)
                    analysis = await streaming_handler.stream_response(analysis_prompt, show_stats=False)
                except ImportError:
                    # Fallback if streaming handler not available
                    async for chunk in llm_client.stream_completion(analysis_prompt):
                        print(chunk, end='', flush=True)
                    print()  # New line after streaming
            else:
                # Show built-in analysis based on actual content
                console.print(Panel(analysis_result, title="🤖 Content Analysis", border_style="blue"))
            
            return f"✅ File analysis completed for {file_path.name}"
            
        except Exception as e:
            error_msg = f"❌ Error in file-search: {e}"
            console.print(error_msg)
            return error_msg
    
    async def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with encoding detection - ACTUAL IMPLEMENTATION"""
        try:
            # Try common encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    # Validate that content was read properly
                    if content is not None:
                        return content
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            # If all encodings fail, read as binary and decode safely
            with open(file_path, 'rb') as f:
                binary_content = f.read()
                return binary_content.decode('utf-8', errors='replace')
                
        except Exception as e:
            console.print(f"❌ Error reading file {file_path}: {e}")
            return None
    
    async def _generate_content_analysis(self, content: str, file_info: Dict[str, Any], file_path: Path) -> str:
        """Generate analysis based on ACTUAL file content"""
        try:
            lines = content.split('\n')
            words = content.split()
            
            # Basic statistics
            stats = {
                'char_count': len(content),
                'line_count': len(lines),
                'word_count': len(words),
                'empty_lines': sum(1 for line in lines if not line.strip()),
                'max_line_length': max(len(line) for line in lines) if lines else 0,
                'avg_line_length': len(content) / len(lines) if lines else 0
            }
            
            # Content type analysis
            content_lower = content.lower()
            content_analysis = self._analyze_file_content_type(content, content_lower, file_info['type'])
            
            # Pattern detection
            patterns = self._detect_content_patterns(content, content_lower)
            
            # Generate suggestions
            suggestions = self._generate_content_suggestions(content, file_info, patterns)
            
            # Build analysis report
            analysis = f"""
📋 **File Analysis Summary**

**File Details:**
• Name: {file_path.name}
• Type: {file_info['type']}
• Size: {file_info['size_human']} ({stats['char_count']} characters)
• Lines: {stats['line_count']} (including {stats['empty_lines']} empty lines)
• Words: {stats['word_count']}

**Content Analysis:**
{content_analysis}

**File Structure:**
• Average line length: {stats['avg_line_length']:.1f} characters
• Longest line: {stats['max_line_length']} characters
• Content density: {'High' if stats['word_count'] > 500 else 'Medium' if stats['word_count'] > 100 else 'Low'}

**Detected Patterns:**
{chr(10).join(f'• {pattern}' for pattern in patterns)}

**Content Preview (first 5 lines):**
{chr(10).join(f'{i+1:2d}: {line}' for i, line in enumerate(lines[:5]))}
{('...' if len(lines) > 5 else '')}

**Suggestions:**
{chr(10).join(f'• {suggestion}' for suggestion in suggestions)}
"""
            return analysis
            
        except Exception as e:
            return f"❌ Error analyzing content: {e}"
    
    def _analyze_file_content_type(self, content: str, content_lower: str, file_type: str) -> str:
        """Analyze what type of content the file actually contains"""
        if file_type == 'text':
            if 'git clone' in content_lower:
                return "This appears to be a Git setup/installation guide with repository cloning instructions."
            elif any(keyword in content_lower for keyword in ['todo', 'task', '- [ ]', '[ ]']):
                return "This appears to be a TODO list or task tracking file."
            elif any(keyword in content_lower for keyword in ['note', 'readme', 'documentation']):
                return "This appears to be a documentation or notes file."
            elif content.count('\n') < 5 and len(content) < 200:
                return "This appears to be a short text snippet or memo."
            else:
                return "This appears to be a general text document."
        
        elif file_type == 'python':
            functions = content.count('def ')
            classes = content.count('class ')
            imports = content.count('import ')
            
            if classes > 0:
                return f"Python module with {classes} class(es) and {functions} function(s)."
            elif functions > 0:
                return f"Python script with {functions} function(s) and {imports} import(s)."
            else:
                return "Python script file."
        
        elif file_type == 'json':
            try:
                json.loads(content)
                return "Valid JSON data file."
            except:
                return "JSON file with potential syntax errors."
        
        elif file_type == 'markdown':
            headers = content.count('#')
            links = content.count('[')
            return f"Markdown document with {headers} header(s) and {links} potential link(s)."
        
        else:
            return f"File of type: {file_type}"
    
    def _detect_content_patterns(self, content: str, content_lower: str) -> List[str]:
        """Detect specific patterns in the actual content"""
        patterns = []
        
        # Git/Development patterns
        if 'git clone' in content_lower:
            patterns.append("Git repository cloning instructions")
        if any(cmd in content_lower for cmd in ['pip install', 'npm install', 'bun install']):
            patterns.append("Package installation commands")
        if any(env in content_lower for env in ['.venv', 'activate', 'virtualenv']):
            patterns.append("Virtual environment setup")
        if any(server in content_lower for server in ['python app.py', 'npm start', 'bun run']):
            patterns.append("Application startup commands")
        
        # Content patterns
        if '@' in content and '.' in content:
            patterns.append("Contains email addresses or mentions")
        if any(url in content_lower for url in ['http://', 'https://', 'www.']):
            patterns.append("Contains web URLs")
        if any(sensitive in content_lower for sensitive in ['password', 'secret', 'key', 'token']):
            patterns.append("⚠️ May contain sensitive information")
        
        # Structure patterns
        if content.count('\n') > 50:
            patterns.append("Large file with extensive content")
        if len(content.split()) > 500:
            patterns.append("Content-heavy document")
        if not content.strip():
            patterns.append("⚠️ File is empty or contains only whitespace")
        
        # Code patterns
        if any(lang in content_lower for lang in ['python', 'javascript', 'html', 'css']):
            patterns.append("References programming languages")
        if any(framework in content_lower for framework in ['flask', 'django', 'react', 'vue']):
            patterns.append("References web frameworks")
        
        return patterns if patterns else ["No special patterns detected"]
    
    def _generate_content_suggestions(self, content: str, file_info: Dict[str, Any], patterns: List[str]) -> List[str]:
        """Generate suggestions based on actual content analysis"""
        suggestions = []
        
        # Git/Setup related suggestions
        if "Git repository cloning instructions" in patterns:
            suggestions.append("Consider adding error handling for failed git clone operations")
            suggestions.append("Add verification steps to check if installation was successful")
        
        if "Package installation commands" in patterns:
            suggestions.append("Consider creating a requirements.txt or package.json file")
            suggestions.append("Add version specifications for better reproducibility")
        
        if "Virtual environment setup" in patterns:
            suggestions.append("Document which Python version is required")
            suggestions.append("Add troubleshooting steps for environment activation issues")
        
        if "Application startup commands" in patterns:
            suggestions.append("Include port numbers and access URLs in startup instructions")
            suggestions.append("Add stopping/shutdown procedures")
        
        # File quality suggestions
        if file_info.get('lines', 0) < 5:
            suggestions.append("File seems quite short - consider adding more detailed instructions")
        
        if "⚠️ May contain sensitive information" in patterns:
            suggestions.append("⚠️ Review and remove any sensitive information before sharing")
        
        # General suggestions
        if file_info['type'] == 'text' and not any('README' in content.upper() for content in [content]):
            suggestions.append("Consider adding a header or title to clarify the file's purpose")
        
        if '\r\n' in content:
            suggestions.append("File uses Windows line endings - consider normalizing for cross-platform compatibility")
        
        return suggestions if suggestions else ["Content appears well-structured"]
    
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

