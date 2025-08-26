#!/usr/bin/env python3
"""
Real-time Code Analysis System
Live code feedback with file watching and incremental suggestions
"""

import asyncio
import ast
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import re

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

console = Console()


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""
    file_path: str
    line_number: int
    column: int
    severity: str  # "error", "warning", "info", "suggestion"
    category: str  # "syntax", "style", "performance", "security", "maintainability"
    message: str
    suggestion: str = ""
    rule_id: str = ""


@dataclass
class AnalysisResult:
    """Result of code analysis"""
    file_path: str
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class CodeAnalyzer:
    """Analyzes code for various issues and improvements"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, Callable]:
        """Initialize analysis rules"""
        return {
            "syntax_check": self._check_syntax,
            "style_check": self._check_style,
            "performance_check": self._check_performance,
            "security_check": self._check_security,
            "maintainability_check": self._check_maintainability,
            "complexity_check": self._check_complexity
        }
    
    async def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = AnalysisResult(file_path=str(file_path))
            
            # Run all analysis rules
            for rule_name, rule_func in self.rules.items():
                try:
                    issues = await rule_func(content, file_path)
                    result.issues.extend(issues)
                except Exception as e:
                    console.print(f"[red]Error in {rule_name}: {e}[/red]")
            
            # Calculate metrics
            result.metrics = self._calculate_metrics(content, result.issues)
            
            return result
            
        except Exception as e:
            console.print(f"[red]Error analyzing {file_path}: {e}[/red]")
            return AnalysisResult(file_path=str(file_path))
    
    async def _check_syntax(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Check for syntax errors"""
        issues = []
        
        if file_path.suffix == '.py':
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=e.lineno or 1,
                    column=e.offset or 0,
                    severity="error",
                    category="syntax",
                    message=f"Syntax error: {e.msg}",
                    rule_id="syntax_error"
                ))
        
        return issues
    
    async def _check_style(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Check for style issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 88:
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    column=88,
                    severity="warning",
                    category="style",
                    message=f"Line too long ({len(line)} > 88 characters)",
                    suggestion="Consider breaking this line into multiple lines",
                    rule_id="line_too_long"
                ))
            
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    column=len(line.rstrip()),
                    severity="info",
                    category="style",
                    message="Trailing whitespace",
                    suggestion="Remove trailing whitespace",
                    rule_id="trailing_whitespace"
                ))
            
            # Multiple blank lines
            if i > 1 and not line.strip() and not lines[i-2].strip():
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    column=0,
                    severity="info",
                    category="style",
                    message="Multiple blank lines",
                    suggestion="Use single blank line",
                    rule_id="multiple_blank_lines"
                ))
        
        return issues
    
    async def _check_performance(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Check for performance issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Inefficient string concatenation
            if '+=' in line and 'str' in line.lower():
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    column=line.find('+='),
                    severity="suggestion",
                    category="performance",
                    message="Inefficient string concatenation",
                    suggestion="Consider using join() or f-strings for better performance",
                    rule_id="inefficient_string_concat"
                ))
            
            # Global variable access in loops
            if re.search(r'for\s+\w+\s+in.*global', line):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    column=0,
                    severity="suggestion",
                    category="performance",
                    message="Global variable access in loop",
                    suggestion="Consider caching global variables locally",
                    rule_id="global_in_loop"
                ))
        
        return issues
    
    async def _check_security(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Check for security issues"""
        issues = []
        lines = content.split('\n')
        
        security_patterns = [
            (r'eval\s*\(', "Use of eval() is dangerous", "Consider safer alternatives"),
            (r'exec\s*\(', "Use of exec() is dangerous", "Consider safer alternatives"),
            (r'input\s*\(.*\)', "Raw input() usage", "Validate and sanitize user input"),
            (r'shell=True', "Shell injection risk", "Avoid shell=True or sanitize input"),
            (r'pickle\.loads?', "Pickle deserialization risk", "Use safer serialization formats"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, suggestion in security_patterns:
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i,
                        column=0,
                        severity="warning",
                        category="security",
                        message=message,
                        suggestion=suggestion,
                        rule_id=f"security_{pattern[:10]}"
                    ))
        
        return issues
    
    async def _check_maintainability(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Check for maintainability issues"""
        issues = []
        
        # Function length
        if file_path.suffix == '.py':
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno + 1
                        if func_lines > 50:
                            issues.append(CodeIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                                severity="suggestion",
                                category="maintainability",
                                message=f"Function '{node.name}' is too long ({func_lines} lines)",
                                suggestion="Consider breaking this function into smaller functions",
                                rule_id="long_function"
                            ))
            except:
                pass
        
        return issues
    
    async def _check_complexity(self, content: str, file_path: Path) -> List[CodeIssue]:
        """Check for complexity issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Nested conditions
            indent_level = len(line) - len(line.lstrip())
            if indent_level > 16 and any(keyword in line for keyword in ['if', 'for', 'while', 'try']):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=i,
                    column=0,
                    severity="suggestion",
                    category="maintainability",
                    message="High nesting level detected",
                    suggestion="Consider extracting nested logic into separate functions",
                    rule_id="high_nesting"
                ))
        
        return issues
    
    def _calculate_metrics(self, content: str, issues: List[CodeIssue]) -> Dict[str, Any]:
        """Calculate code metrics"""
        lines = content.split('\n')
        
        return {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "total_issues": len(issues),
            "errors": len([issue for issue in issues if issue.severity == "error"]),
            "warnings": len([issue for issue in issues if issue.severity == "warning"]),
            "suggestions": len([issue for issue in issues if issue.severity == "suggestion"]),
            "info": len([issue for issue in issues if issue.severity == "info"]),
        }


class FileWatcher(FileSystemEventHandler):
    """Watches files for changes and triggers analysis"""

    def __init__(self, analyzer: CodeAnalyzer, callback: Callable[[AnalysisResult], None], loop: asyncio.AbstractEventLoop = None):
        self.analyzer = analyzer
        self.callback = callback
        self.debounce_time = 1.0  # 1 second debounce
        self.pending_files: Dict[str, float] = {}
        self.loop = loop  # Store reference to the main event loop

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            file_path = Path(event.src_path)

            # Only analyze code files
            if file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs']:
                current_time = time.time()
                self.pending_files[str(file_path)] = current_time

                # Schedule analysis using the main event loop
                if self.loop and not self.loop.is_closed():
                    try:
                        # Use run_coroutine_threadsafe to schedule from watchdog thread
                        asyncio.run_coroutine_threadsafe(
                            self._debounced_analysis(file_path, current_time),
                            self.loop
                        )
                    except Exception as e:
                        console.print(f"[red]Error scheduling analysis: {e}[/red]")
                else:
                    console.print("[yellow]⚠️ Event loop not available for analysis[/yellow]")
    
    async def _debounced_analysis(self, file_path: Path, trigger_time: float):
        """Perform analysis after debounce period"""
        await asyncio.sleep(self.debounce_time)
        
        # Check if this is still the latest trigger for this file
        if self.pending_files.get(str(file_path)) == trigger_time:
            try:
                result = await self.analyzer.analyze_file(file_path)
                self.callback(result)
            except Exception as e:
                console.print(f"[red]Error analyzing {file_path}: {e}[/red]")
            finally:
                # Clean up
                self.pending_files.pop(str(file_path), None)


class RealTimeAnalysisEngine:
    """Main engine for real-time code analysis"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.analyzer = CodeAnalyzer()
        self.observer = Observer()
        self.results: Dict[str, AnalysisResult] = {}
        self.is_running = False
        self.live_display: Optional[Live] = None
        self.event_handler = None  # Store reference to event handler

    def start_watching(self, show_live_display: bool = True):
        """Start watching files for changes"""
        if self.is_running:
            console.print("[yellow]⚠️ Real-time analysis is already running[/yellow]")
            return

        console.print(f"🔍 [cyan]Starting real-time code analysis for {self.workspace_path}[/cyan]")

        try:
            # Get the current event loop
            loop = asyncio.get_running_loop()
        except RuntimeError:
            console.print("[red]❌ No running event loop found. Real-time analysis requires an async context.[/red]")
            return

        # Setup file watcher with event loop reference
        self.event_handler = FileWatcher(self.analyzer, self._on_analysis_result, loop)
        self.observer.schedule(self.event_handler, str(self.workspace_path), recursive=True)
        self.observer.start()
        self.is_running = True

        if show_live_display:
            self._start_live_display()

        console.print("✅ [green]Real-time analysis started. Watching for file changes...[/green]")

    def restart_watching(self, show_live_display: bool = True):
        """Restart watching (stop then start)"""
        console.print("🔄 [cyan]Restarting real-time analysis...[/cyan]")
        self.stop_watching()
        # Small delay to ensure cleanup
        import time
        time.sleep(0.5)
        self.start_watching(show_live_display)

    def stop_watching(self):
        """Stop watching files"""
        if not self.is_running:
            console.print("[yellow]⚠️ Real-time analysis is not running[/yellow]")
            return

        console.print("⏹️ [cyan]Stopping real-time analysis...[/cyan]")

        try:
            # Stop the observer
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join(timeout=5.0)  # Wait max 5 seconds

            # Clean up references
            self.event_handler = None
            self.is_running = False

            # Stop live display
            if self.live_display:
                self.live_display.stop()
                self.live_display = None

            console.print("✅ [green]Real-time analysis stopped successfully[/green]")

        except Exception as e:
            console.print(f"[red]Error stopping analysis: {e}[/red]")
            # Force cleanup
            self.is_running = False
            self.event_handler = None
    
    def _on_analysis_result(self, result: AnalysisResult):
        """Handle analysis result"""
        self.results[result.file_path] = result
        
        # Show immediate feedback for errors
        errors = [issue for issue in result.issues if issue.severity == "error"]
        if errors:
            console.print(f"❌ [red]{len(errors)} error(s) found in {Path(result.file_path).name}[/red]")
            for error in errors[:3]:  # Show first 3 errors
                console.print(f"   Line {error.line_number}: {error.message}")
    
    def _start_live_display(self):
        """Start live display of analysis results"""
        def generate_display():
            return self._create_summary_panel()
        
        self.live_display = Live(generate_display(), refresh_per_second=1, console=console)
        self.live_display.start()
    
    def _create_summary_panel(self) -> Panel:
        """Create summary panel for live display"""
        if not self.results:
            return Panel("No files analyzed yet", title="📊 Real-time Analysis", border_style="blue")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan")
        table.add_column("Errors", style="red")
        table.add_column("Warnings", style="yellow")
        table.add_column("Suggestions", style="green")
        table.add_column("Last Updated", style="dim")
        
        for file_path, result in sorted(self.results.items()):
            file_name = Path(file_path).name
            errors = len([i for i in result.issues if i.severity == "error"])
            warnings = len([i for i in result.issues if i.severity == "warning"])
            suggestions = len([i for i in result.issues if i.severity == "suggestion"])
            
            last_updated = time.strftime("%H:%M:%S", time.localtime(result.timestamp))
            
            table.add_row(
                file_name,
                str(errors) if errors > 0 else "✅",
                str(warnings) if warnings > 0 else "✅",
                str(suggestions) if suggestions > 0 else "✅",
                last_updated
            )
        
        return Panel(table, title="📊 Real-time Code Analysis", border_style="blue")
    
    async def analyze_workspace(self) -> Dict[str, AnalysisResult]:
        """Analyze all files in workspace"""
        console.print("🔍 [cyan]Analyzing workspace...[/cyan]")
        
        code_files = []
        for pattern in ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"]:
            code_files.extend(self.workspace_path.glob(pattern))
        
        results = {}
        for file_path in code_files:
            if file_path.is_file():
                result = await self.analyzer.analyze_file(file_path)
                results[str(file_path)] = result
                self.results[str(file_path)] = result
        
        console.print(f"✅ [green]Analyzed {len(results)} files[/green]")
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        if not self.results:
            return {}
        
        total_issues = sum(len(result.issues) for result in self.results.values())
        total_errors = sum(len([i for i in result.issues if i.severity == "error"]) for result in self.results.values())
        total_warnings = sum(len([i for i in result.issues if i.severity == "warning"]) for result in self.results.values())
        total_suggestions = sum(len([i for i in result.issues if i.severity == "suggestion"]) for result in self.results.values())
        
        return {
            "files_analyzed": len(self.results),
            "total_issues": total_issues,
            "errors": total_errors,
            "warnings": total_warnings,
            "suggestions": total_suggestions,
            "files_with_errors": len([r for r in self.results.values() if any(i.severity == "error" for i in r.issues)])
        }


# Global instance
realtime_analyzer = RealTimeAnalysisEngine()
