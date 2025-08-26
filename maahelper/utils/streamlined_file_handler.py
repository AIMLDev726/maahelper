#!/usr/bin/env python3
"""
Streamlined File Handler with File Search
Optimized for directory structure display and file search with AI processing
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import aiofiles

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

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
        

    def is_supported_file(self, filename: str) -> bool:
        """Check if file type is supported"""
        from pathlib import Path
        return Path(filename).suffix in self.SUPPORTED_EXTENSIONS

    def detect_language(self, filename: str) -> str:
        """Detect language from file extension"""
        from pathlib import Path
        return self.SUPPORTED_EXTENSIONS.get(Path(filename).suffix, 'text')

    def scan_workspace(self, workspace_path: str = None, extensions: list = None) -> list:
        """Scan workspace for supported files"""
        if workspace_path is None:
            workspace_path = str(self.workspace_path)
        
        workspace = Path(workspace_path)
        if not workspace.exists():
            return []
        
        files = []
        search_extensions = extensions or list(self.SUPPORTED_EXTENSIONS.keys())
        
        for ext in search_extensions:
            pattern = f"**/*{ext}"
            for file_path in workspace.glob(pattern):
                if file_path.is_file():
                    files.append(str(file_path))
        
        return files

    def analyze_file(self, file_path: str) -> dict:
        """Analyze a single file"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": "File not found"}
            
            if not path.is_file():
                return {"error": "Not a file"}
            
            content = path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                "file_path": str(path),
                "language": self.detect_language(path.name),
                "content": content,
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        except Exception as e:
            return {"error": str(e)}
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
            stat = file_path.stat()
            console.print(Panel.fit(
                f"[bold green]📁 File: {file_path.name}[/bold green]\n"
                f"[cyan]Type:[/cyan] {file_info['type']}\n"
                f"[cyan]Size:[/cyan] {file_info['size_human']} ({file_info['size']} bytes)\n"
                f"[cyan]Lines:[/cyan] {file_info.get('lines', 'N/A')}\n"
                f"[cyan]Path:[/cyan] {file_path}\n"
                f"[cyan]Created:[/cyan] {datetime.fromtimestamp(getattr(stat, 'st_birthtime', stat.st_ctime))}\n"
                f"[cyan]Modified:[/cyan] {datetime.fromtimestamp(stat.st_mtime)}",
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

            # Built-in analysis based on actual content
            analysis_result = self._analyze_file_content(content, file_info)

            # Check if we have a real LLM client
            if hasattr(llm_client, 'stream_completion'):
                console.print("🔍 [bold cyan]AI Analysis:[/bold cyan]")
                try:
                    # Use streaming for real-time response
                    from .streaming import ModernStreamingHandler
                    streaming_handler = ModernStreamingHandler(llm_client)
                    await streaming_handler.stream_response(analysis_prompt, show_stats=False)
                except (ImportError, AttributeError, Exception) as e:
                    # Fallback if streaming handler not available or fails
                    console.print(f"[yellow]Note: Using fallback analysis (streaming unavailable: {e})[/yellow]")
                    try:
                        async for chunk in llm_client.stream_completion(analysis_prompt):
                            print(chunk, end='', flush=True)
                        print()  # New line after streaming
                    except Exception as stream_error:
                        console.print(f"[red]Streaming failed: {stream_error}[/red]")
                        console.print(Panel(analysis_result, title="🤖 Content Analysis (Fallback)", border_style="blue"))
            else:
                # Show built-in analysis based on actual content
                console.print(Panel(analysis_result, title="🤖 Content Analysis", border_style="blue"))

            return f"✅ File analysis completed for {file_path.name}"

        except Exception as e:
            error_msg = f"❌ Error in file-search: {e}"
            console.print(error_msg)
            return error_msg

    async def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content with encoding detection"""
        try:
            # Try UTF-8 first
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    return await f.read()
            except UnicodeDecodeError:
                # Fallback to chardet for encoding detection
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding']
                    if encoding:
                        return raw_data.decode(encoding)
                    else:
                        return raw_data.decode('utf-8', errors='ignore')
        except Exception as e:
            console.print(f"[red]Error reading file {file_path}: {e}[/red]")
            return None

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information"""
        try:
            stat = file_path.stat()
            file_size = stat.st_size

            # Determine file type
            file_type = "unknown"
            if file_path.suffix in self.SUPPORTED_EXTENSIONS:
                file_type = self.SUPPORTED_EXTENSIONS[file_path.suffix]

            # Count lines for text files
            lines = 0
            if file_type in ['python', 'javascript', 'typescript', 'text', 'markdown']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = sum(1 for _ in f)
                except:
                    lines = 0

            return {
                'type': file_type,
                'size': file_size,
                'size_human': self._format_file_size(file_size),
                'lines': lines if lines > 0 else None
            }
        except Exception as e:
            return {
                'type': 'unknown',
                'size': 0,
                'size_human': '0 B',
                'lines': None
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def _analyze_file_content(self, content: str, file_info: Dict[str, Any]) -> str:
        """Analyze file content and provide insights"""
        analysis = []

        # Basic statistics
        lines = content.count('\n') + 1
        words = len(content.split())
        chars = len(content)

        analysis.append(f"**File Statistics:**")
        analysis.append(f"- Lines: {lines:,}")
        analysis.append(f"- Words: {words:,}")
        analysis.append(f"- Characters: {chars:,}")
        analysis.append(f"- Size: {file_info['size_human']}")

        # Content analysis based on file type
        file_type = file_info.get('type', 'unknown')

        if file_type == 'python':
            analysis.extend(self._analyze_python_content(content))
        elif file_type in ['javascript', 'typescript']:
            analysis.extend(self._analyze_js_content(content))
        elif file_type == 'json':
            analysis.extend(self._analyze_json_content(content))
        elif file_type == 'markdown':
            analysis.extend(self._analyze_markdown_content(content))
        else:
            analysis.extend(self._analyze_generic_content(content))

        return '\n'.join(analysis)

    def _analyze_python_content(self, content: str) -> List[str]:
        """Analyze Python file content"""
        analysis = []

        # Count imports, functions, classes
        import_count = content.count('import ') + content.count('from ')
        function_count = content.count('def ')
        class_count = content.count('class ')

        analysis.append(f"\n**Python Analysis:**")
        analysis.append(f"- Imports: {import_count}")
        analysis.append(f"- Functions: {function_count}")
        analysis.append(f"- Classes: {class_count}")

        # Check for common patterns
        if 'async def' in content:
            analysis.append("- Contains async functions")
        if '__main__' in content:
            analysis.append("- Has main execution block")
        if 'try:' in content:
            analysis.append("- Uses exception handling")

        return analysis

    def _analyze_js_content(self, content: str) -> List[str]:
        """Analyze JavaScript/TypeScript content"""
        analysis = []

        function_count = content.count('function ') + content.count('=>')
        const_count = content.count('const ')
        let_count = content.count('let ')

        analysis.append(f"\n**JavaScript/TypeScript Analysis:**")
        analysis.append(f"- Functions: {function_count}")
        analysis.append(f"- Constants: {const_count}")
        analysis.append(f"- Variables: {let_count}")

        if 'import ' in content:
            analysis.append("- Uses ES6 imports")
        if 'async ' in content:
            analysis.append("- Contains async functions")

        return analysis

    def _analyze_json_content(self, content: str) -> List[str]:
        """Analyze JSON content"""
        analysis = []

        try:
            import json
            data = json.loads(content)

            analysis.append(f"\n**JSON Analysis:**")
            analysis.append(f"- Valid JSON: ✅")

            if isinstance(data, dict):
                analysis.append(f"- Keys: {len(data)}")
            elif isinstance(data, list):
                analysis.append(f"- Items: {len(data)}")

        except json.JSONDecodeError:
            analysis.append(f"\n**JSON Analysis:**")
            analysis.append(f"- Valid JSON: ❌")

        return analysis

    def _analyze_markdown_content(self, content: str) -> List[str]:
        """Analyze Markdown content"""
        analysis = []

        heading_count = content.count('#')
        link_count = content.count('[')
        code_block_count = content.count('```')

        analysis.append(f"\n**Markdown Analysis:**")
        analysis.append(f"- Headings: {heading_count}")
        analysis.append(f"- Links: {link_count}")
        analysis.append(f"- Code blocks: {code_block_count // 2}")

        return analysis

    def _analyze_generic_content(self, content: str) -> List[str]:
        """Analyze generic text content"""
        analysis = []

        # Basic text analysis
        sentences = content.count('.') + content.count('!') + content.count('?')
        paragraphs = content.count('\n\n') + 1

        analysis.append(f"\n**Content Analysis:**")
        analysis.append(f"- Sentences: ~{sentences}")
        analysis.append(f"- Paragraphs: ~{paragraphs}")

        return analysis

    def show_supported_files_table(self):
        """Show supported file types in a table format"""
        from rich.table import Table

        table = Table(title="📁 Supported File Types", show_header=True, header_style="bold magenta")
        table.add_column("Extension", style="cyan", width=12)
        table.add_column("Type", style="green", width=15)
        table.add_column("Icon", style="yellow", width=6)
        table.add_column("Description", style="white", width=40)

        descriptions = {
            'python': 'Python source code files',
            'javascript': 'JavaScript source files',
            'typescript': 'TypeScript source files',
            'html': 'HTML markup files',
            'css': 'Cascading Style Sheets',
            'json': 'JSON data files',
            'yaml': 'YAML configuration files',
            'csv': 'Comma-separated values',
            'markdown': 'Markdown documentation',
            'text': 'Plain text files',
            'pdf': 'PDF documents',
            'docx': 'Word documents',
            'database': 'Database files',
            'log': 'Log files'
        }

        for ext, file_type in self.SUPPORTED_EXTENSIONS.items():
            icon = self._get_file_icon(file_type)
            description = descriptions.get(file_type, 'Supported file type')
            table.add_row(ext, file_type.title(), icon, description)

        console.print()
        console.print(table)
        console.print()
        console.print(f"[dim]Total supported extensions: {len(self.SUPPORTED_EXTENSIONS)}[/dim]")

    def list_supported_files(self, max_files: int = 50) -> List[Dict[str, Any]]:
        """List supported files in the workspace"""
        supported_files = []

        try:
            # Search for supported files
            for ext in self.SUPPORTED_EXTENSIONS.keys():
                pattern = f"**/*{ext}"
                for file_path in self.workspace_path.glob(pattern):
                    if file_path.is_file() and len(supported_files) < max_files:
                        try:
                            stat = file_path.stat()
                            file_info = {
                                'path': str(file_path),
                                'name': file_path.name,
                                'type': self.SUPPORTED_EXTENSIONS.get(file_path.suffix, 'unknown'),
                                'size': stat.st_size,
                                'size_human': self._format_file_size(stat.st_size),
                                'modified': datetime.fromtimestamp(stat.st_mtime),
                                'extension': file_path.suffix
                            }
                            supported_files.append(file_info)
                        except (OSError, PermissionError):
                            continue

            # Sort by modification time (newest first)
            supported_files.sort(key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            console.print(f"[red]Error listing files: {e}[/red]")

        return supported_files


# Global file handler instance
file_handler = StreamlinedFileHandler()
