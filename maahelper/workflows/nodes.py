"""
Workflow Nodes for MaaHelper
Individual node implementations for workflow execution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import subprocess
import json

from rich.console import Console

from ..core.llm_client import UnifiedLLMClient
from ..vibecoding.commands import VibecodingCommands
from ..utils.streamlined_file_handler import file_handler

console = Console()
logger = logging.getLogger(__name__)

class WorkflowNodes:
    """
    Collection of workflow nodes for different types of tasks
    Each node represents a specific operation that can be performed in a workflow
    """
    
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        self.llm_client = llm_client
        self.vibecoding = VibecodingCommands(llm_client) if llm_client else None
        
        # Register available nodes
        self.nodes: Dict[str, Callable] = {
            # Code analysis nodes
            'analyze_file': self.analyze_file_node,
            'code_review': self.code_review_node,
            'bug_analysis': self.bug_analysis_node,
            'performance_analysis': self.performance_analysis_node,
            
            # Code generation nodes
            'generate_code': self.generate_code_node,
            'refactor_code': self.refactor_code_node,
            'generate_tests': self.generate_tests_node,
            'generate_docs': self.generate_docs_node,
            
            # File operations
            'read_file': self.read_file_node,
            'write_file': self.write_file_node,
            'create_directory': self.create_directory_node,
            'copy_file': self.copy_file_node,
            
            # Git operations
            'git_commit': self.git_commit_node,
            'git_branch': self.git_branch_node,
            'git_merge': self.git_merge_node,
            
            # Project operations
            'scan_project': self.scan_project_node,
            'run_tests': self.run_tests_node,
            'build_project': self.build_project_node,
            'deploy_project': self.deploy_project_node,
            
            # AI operations
            'ai_chat': self.ai_chat_node,
            'ai_analyze': self.ai_analyze_node,
            'ai_generate': self.ai_generate_node,
            
            # Utility nodes
            'sleep': self.sleep_node,
            'log_message': self.log_message_node,
            'conditional': self.conditional_node,
            'parallel': self.parallel_node
        }
    
    async def execute_node(self, node_type: str, inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a specific node type with given inputs"""
        if node_type not in self.nodes:
            logger.error(f"Unknown node type: {node_type}")
            return None
        
        try:
            console.print(f"[cyan]🔄 Executing node: {node_type}[/cyan]")
            result = await self.nodes[node_type](inputs)
            console.print(f"[green]✅ Node {node_type} completed[/green]")
            return result
        except Exception as e:
            logger.error(f"Node execution failed for {node_type}: {e}")
            console.print(f"[red]❌ Node {node_type} failed: {e}[/red]")
            return None
    
    def get_available_nodes(self) -> List[str]:
        """Get list of available node types"""
        return list(self.nodes.keys())
    
    # Code Analysis Nodes
    async def analyze_file_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single file"""
        file_path = inputs.get('file_path')
        if not file_path:
            raise ValueError("file_path is required")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path_obj.read_text(encoding='utf-8')
        
        return {
            'file_path': str(file_path_obj),
            'content': content,
            'size': len(content),
            'lines': len(content.split('\n')),
            'language': self._detect_language(file_path_obj.suffix)
        }
    
    async def code_review_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI-powered code review"""
        if not self.vibecoding:
            raise ValueError("LLM client not available for code review")
        
        code = inputs.get('code') or inputs.get('content')
        language = inputs.get('language', 'python')
        context = inputs.get('context', '')
        
        if not code:
            raise ValueError("code or content is required")
        
        result = await self.vibecoding.code_review(code, language, context)
        
        return {
            'review_result': result,
            'language': language,
            'reviewed_at': str(asyncio.get_event_loop().time())
        }
    
    async def bug_analysis_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform bug analysis"""
        if not self.vibecoding:
            raise ValueError("LLM client not available for bug analysis")
        
        code = inputs.get('code') or inputs.get('content')
        language = inputs.get('language', 'python')
        error_context = inputs.get('error_context', '')
        
        if not code:
            raise ValueError("code or content is required")
        
        result = await self.vibecoding.bug_analysis(code, language, error_context)
        
        return {
            'bug_analysis': result,
            'language': language,
            'analyzed_at': str(asyncio.get_event_loop().time())
        }
    
    async def performance_analysis_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform performance analysis"""
        if not self.vibecoding:
            raise ValueError("LLM client not available for performance analysis")
        
        code = inputs.get('code') or inputs.get('content')
        language = inputs.get('language', 'python')
        focus_areas = inputs.get('focus_areas', '')
        
        if not code:
            raise ValueError("code or content is required")
        
        result = await self.vibecoding.optimize_performance(code, language, focus_areas)
        
        return {
            'performance_analysis': result,
            'language': language,
            'analyzed_at': str(asyncio.get_event_loop().time())
        }
    
    # Code Generation Nodes
    async def generate_code_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        if not self.vibecoding:
            raise ValueError("LLM client not available for code generation")
        
        requirements = inputs.get('requirements')
        language = inputs.get('language', 'python')
        context = inputs.get('context', '')
        
        if not requirements:
            raise ValueError("requirements is required")
        
        result = await self.vibecoding.implement_feature(requirements, language, context)
        
        return {
            'generated_code': result,
            'language': language,
            'requirements': requirements,
            'generated_at': str(asyncio.get_event_loop().time())
        }
    
    async def refactor_code_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor existing code"""
        if not self.vibecoding:
            raise ValueError("LLM client not available for refactoring")
        
        code = inputs.get('code') or inputs.get('content')
        language = inputs.get('language', 'python')
        refactor_goals = inputs.get('refactor_goals', 'improve code quality')
        
        if not code:
            raise ValueError("code or content is required")
        
        result = await self.vibecoding.refactor_code(code, language, refactor_goals)
        
        return {
            'refactored_code': result,
            'original_code': code,
            'language': language,
            'refactored_at': str(asyncio.get_event_loop().time())
        }
    
    async def generate_tests_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tests for code"""
        if not self.vibecoding:
            raise ValueError("LLM client not available for test generation")
        
        code = inputs.get('code') or inputs.get('content')
        language = inputs.get('language', 'python')
        test_framework = inputs.get('test_framework', 'pytest')
        
        if not code:
            raise ValueError("code or content is required")
        
        # Use implement_feature for test generation
        requirements = f"Generate comprehensive tests for the following {language} code using {test_framework}:\n\n{code}"
        result = await self.vibecoding.implement_feature(requirements, language)
        
        return {
            'generated_tests': result,
            'original_code': code,
            'test_framework': test_framework,
            'language': language,
            'generated_at': str(asyncio.get_event_loop().time())
        }
    
    async def generate_docs_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for code"""
        if not self.llm_client:
            raise ValueError("LLM client not available for documentation generation")
        
        code = inputs.get('code') or inputs.get('content')
        language = inputs.get('language', 'python')
        doc_format = inputs.get('doc_format', 'markdown')
        
        if not code:
            raise ValueError("code or content is required")
        
        prompt = f"""
        Generate comprehensive documentation for this {language} code in {doc_format} format:
        
        {code}
        
        Include:
        - Overview and purpose
        - Function/class descriptions
        - Parameters and return values
        - Usage examples
        - Any important notes or warnings
        """
        
        result = await self.llm_client.achat_completion([
            {"role": "user", "content": prompt}
        ])
        
        return {
            'generated_docs': result,
            'original_code': code,
            'doc_format': doc_format,
            'language': language,
            'generated_at': str(asyncio.get_event_loop().time())
        }
    
    # File Operation Nodes
    async def read_file_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Read content from a file"""
        file_path = inputs.get('file_path')
        encoding = inputs.get('encoding', 'utf-8')
        
        if not file_path:
            raise ValueError("file_path is required")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path_obj.read_text(encoding=encoding)
        
        return {
            'file_path': str(file_path_obj),
            'content': content,
            'size': len(content),
            'encoding': encoding
        }
    
    async def write_file_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to a file"""
        file_path = inputs.get('file_path')
        content = inputs.get('content')
        encoding = inputs.get('encoding', 'utf-8')
        create_dirs = inputs.get('create_dirs', True)
        
        if not file_path or content is None:
            raise ValueError("file_path and content are required")
        
        file_path_obj = Path(file_path)
        
        if create_dirs:
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        file_path_obj.write_text(content, encoding=encoding)
        
        return {
            'file_path': str(file_path_obj),
            'bytes_written': len(content.encode(encoding)),
            'encoding': encoding
        }
    
    async def create_directory_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create a directory"""
        dir_path = inputs.get('dir_path')
        parents = inputs.get('parents', True)
        exist_ok = inputs.get('exist_ok', True)
        
        if not dir_path:
            raise ValueError("dir_path is required")
        
        dir_path_obj = Path(dir_path)
        dir_path_obj.mkdir(parents=parents, exist_ok=exist_ok)
        
        return {
            'dir_path': str(dir_path_obj),
            'created': True
        }
    
    async def copy_file_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Copy a file"""
        import shutil
        
        source_path = inputs.get('source_path')
        dest_path = inputs.get('dest_path')
        
        if not source_path or not dest_path:
            raise ValueError("source_path and dest_path are required")
        
        source_path_obj = Path(source_path)
        dest_path_obj = Path(dest_path)
        
        if not source_path_obj.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Create destination directory if needed
        dest_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source_path_obj, dest_path_obj)
        
        return {
            'source_path': str(source_path_obj),
            'dest_path': str(dest_path_obj),
            'copied': True
        }
    
    # Utility Nodes
    async def sleep_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Sleep for specified duration"""
        duration = inputs.get('duration', 1.0)
        await asyncio.sleep(duration)
        
        return {
            'slept_duration': duration
        }
    
    async def log_message_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Log a message"""
        message = inputs.get('message', '')
        level = inputs.get('level', 'info')
        
        if level == 'error':
            logger.error(message)
            console.print(f"[red]❌ {message}[/red]")
        elif level == 'warning':
            logger.warning(message)
            console.print(f"[yellow]⚠️ {message}[/yellow]")
        else:
            logger.info(message)
            console.print(f"[blue]ℹ️ {message}[/blue]")
        
        return {
            'message': message,
            'level': level,
            'logged_at': str(asyncio.get_event_loop().time())
        }
    
    async def conditional_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conditional logic"""
        condition = inputs.get('condition')
        true_value = inputs.get('true_value')
        false_value = inputs.get('false_value')
        
        if condition is None:
            raise ValueError("condition is required")
        
        result = true_value if condition else false_value
        
        return {
            'condition': condition,
            'result': result,
            'branch_taken': 'true' if condition else 'false'
        }
    
    async def parallel_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple operations in parallel"""
        operations = inputs.get('operations', [])
        
        if not operations:
            raise ValueError("operations list is required")
        
        # Execute all operations in parallel
        tasks = []
        for i, operation in enumerate(operations):
            node_type = operation.get('node_type')
            node_inputs = operation.get('inputs', {})
            
            if node_type:
                task = self.execute_node(node_type, node_inputs)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            'parallel_results': results,
            'operations_count': len(operations)
        }
    
    # AI Operation Nodes
    async def ai_chat_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI chat completion"""
        if not self.llm_client:
            raise ValueError("LLM client not available")
        
        prompt = inputs.get('prompt')
        system_message = inputs.get('system_message')
        
        if not prompt:
            raise ValueError("prompt is required")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        result = await self.llm_client.achat_completion(messages)
        
        return {
            'ai_response': result,
            'prompt': prompt,
            'system_message': system_message,
            'responded_at': str(asyncio.get_event_loop().time())
        }
    
    async def ai_analyze_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI analysis on data"""
        if not self.llm_client:
            raise ValueError("LLM client not available")
        
        data = inputs.get('data')
        analysis_type = inputs.get('analysis_type', 'general')
        
        if not data:
            raise ValueError("data is required")
        
        prompt = f"""
        Perform {analysis_type} analysis on the following data:
        
        {data}
        
        Provide detailed insights, patterns, and recommendations.
        """
        
        result = await self.llm_client.achat_completion([
            {"role": "user", "content": prompt}
        ])
        
        return {
            'analysis_result': result,
            'analysis_type': analysis_type,
            'original_data': data,
            'analyzed_at': str(asyncio.get_event_loop().time())
        }
    
    async def ai_generate_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using AI"""
        if not self.llm_client:
            raise ValueError("LLM client not available")
        
        prompt = inputs.get('prompt')
        content_type = inputs.get('content_type', 'text')
        
        if not prompt:
            raise ValueError("prompt is required")
        
        full_prompt = f"Generate {content_type} content based on: {prompt}"
        
        result = await self.llm_client.achat_completion([
            {"role": "user", "content": full_prompt}
        ])
        
        return {
            'generated_content': result,
            'content_type': content_type,
            'prompt': prompt,
            'generated_at': str(asyncio.get_event_loop().time())
        }
    
    # Git Operation Nodes (simplified implementations)
    async def git_commit_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create a git commit"""
        message = inputs.get('message', 'Automated commit from MaaHelper workflow')
        add_all = inputs.get('add_all', True)

        try:
            if add_all:
                subprocess.run(['git', 'add', '.'], check=True)

            subprocess.run(['git', 'commit', '-m', message], check=True)

            return {
                'commit_message': message,
                'committed': True
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git commit failed: {e}")

    async def git_branch_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create or switch to a git branch"""
        branch_name = inputs.get('branch_name')
        create_new = inputs.get('create_new', True)

        if not branch_name:
            raise ValueError("branch_name is required")

        try:
            if create_new:
                subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            else:
                subprocess.run(['git', 'checkout', branch_name], check=True)

            return {
                'branch_name': branch_name,
                'created': create_new,
                'switched': True
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git branch operation failed: {e}")

    async def git_merge_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge a git branch"""
        source_branch = inputs.get('source_branch')
        target_branch = inputs.get('target_branch', 'main')

        if not source_branch:
            raise ValueError("source_branch is required")

        try:
            # Switch to target branch
            subprocess.run(['git', 'checkout', target_branch], check=True)

            # Merge source branch
            subprocess.run(['git', 'merge', source_branch], check=True)

            return {
                'source_branch': source_branch,
                'target_branch': target_branch,
                'merged': True
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git merge failed: {e}")
    
    async def scan_project_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Scan project structure"""
        project_path = inputs.get('project_path', '.')
        include_hidden = inputs.get('include_hidden', False)

        project_path_obj = Path(project_path)
        if not project_path_obj.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")

        files = []
        for file_path in project_path_obj.rglob('*'):
            if file_path.is_file():
                if not include_hidden and any(part.startswith('.') for part in file_path.parts):
                    continue
                files.append(str(file_path.relative_to(project_path_obj)))

        return {
            'project_path': str(project_path_obj),
            'files': files,
            'file_count': len(files)
        }

    async def run_tests_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run project tests"""
        test_command = inputs.get('test_command', 'python -m pytest')
        test_path = inputs.get('test_path', 'tests/')

        try:
            result = subprocess.run(
                test_command.split() + [test_path] if test_path else test_command.split(),
                capture_output=True,
                text=True,
                check=False
            )

            return {
                'test_command': test_command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'test_command': test_command,
                'error': str(e),
                'success': False
            }

    async def build_project_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Build the project"""
        build_command = inputs.get('build_command', 'python setup.py build')

        try:
            result = subprocess.run(
                build_command.split(),
                capture_output=True,
                text=True,
                check=False
            )

            return {
                'build_command': build_command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'build_command': build_command,
                'error': str(e),
                'success': False
            }

    async def deploy_project_node(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy the project"""
        deploy_command = inputs.get('deploy_command', 'echo "No deploy command specified"')

        try:
            result = subprocess.run(
                deploy_command.split(),
                capture_output=True,
                text=True,
                check=False
            )

            return {
                'deploy_command': deploy_command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'deploy_command': deploy_command,
                'error': str(e),
                'success': False
            }
    
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
            '.rb': 'ruby'
        }
        return extension_map.get(file_extension.lower(), 'text')
