#!/usr/bin/env python3
"""
Vibecoding Workflow
Orchestrates vibecoding operations and workflow management
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID

from .prompts import vibecoding_prompts
from .commands import vibecoding_commands

console = Console()


class VibecodingWorkflow:
    """Orchestrates vibecoding operations and workflow management"""
    
    def __init__(self, llm_client=None, workspace_path: str = "."):
        self.llm_client = llm_client
        self.workspace_path = Path(workspace_path)
        self.prompts = vibecoding_prompts
        self.commands = vibecoding_commands
        self.commands.llm_client = llm_client
        
        # Workflow state
        self.current_session = {}
        self.workflow_history = []
    
    async def start_coding_session(self, project_description: str, goals: List[str]) -> str:
        """Start a new coding session with goals"""
        session_id = f"session_{len(self.workflow_history) + 1}"
        
        self.current_session = {
            "id": session_id,
            "description": project_description,
            "goals": goals,
            "completed_tasks": [],
            "current_task": None,
            "context": {}
        }
        
        console.print(Panel(
            f"[bold green]🚀 Starting Coding Session[/bold green]\n\n"
            f"[cyan]Project:[/cyan] {project_description}\n"
            f"[cyan]Goals:[/cyan]\n" + "\n".join(f"  • {goal}" for goal in goals),
            title="✨ Vibecoding Session",
            border_style="green"
        ))
        
        return f"✅ Started coding session: {session_id}"
    
    async def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze current project structure"""
        analysis = {
            "files": [],
            "languages": set(),
            "structure": {},
            "suggestions": []
        }
        
        # Scan workspace for code files
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.go', '.rs']
        
        for ext in code_extensions:
            files = list(self.workspace_path.glob(f"**/*{ext}"))
            for file_path in files:
                if file_path.is_file():
                    analysis["files"].append(str(file_path.relative_to(self.workspace_path)))
                    analysis["languages"].add(ext[1:])  # Remove the dot
        
        # Analyze structure
        analysis["structure"] = self._analyze_directory_structure()
        
        # Generate suggestions
        analysis["suggestions"] = await self._generate_project_suggestions(analysis)
        
        return analysis
    
    def _analyze_directory_structure(self) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {
            "has_tests": False,
            "has_docs": False,
            "has_config": False,
            "main_directories": [],
            "depth": 0
        }
        
        # Check for common directories
        common_dirs = ['tests', 'test', 'docs', 'documentation', 'config', 'src', 'lib']
        
        for item in self.workspace_path.iterdir():
            if item.is_dir():
                dir_name = item.name.lower()
                structure["main_directories"].append(item.name)
                
                if any(test_dir in dir_name for test_dir in ['test', 'spec']):
                    structure["has_tests"] = True
                elif any(doc_dir in dir_name for doc_dir in ['doc', 'readme']):
                    structure["has_docs"] = True
                elif 'config' in dir_name:
                    structure["has_config"] = True
        
        return structure
    
    async def _generate_project_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate project improvement suggestions"""
        suggestions = []
        
        # Check for missing components
        if not analysis["structure"]["has_tests"]:
            suggestions.append("Consider adding a tests directory with unit tests")
        
        if not analysis["structure"]["has_docs"]:
            suggestions.append("Add documentation (README.md, API docs)")
        
        if len(analysis["files"]) > 10 and not analysis["structure"]["has_config"]:
            suggestions.append("Consider adding configuration management")
        
        # Language-specific suggestions
        if "python" in analysis["languages"]:
            if not any("requirements" in f for f in analysis["files"]):
                suggestions.append("Add requirements.txt for Python dependencies")
            if not any("__init__" in f for f in analysis["files"]):
                suggestions.append("Consider making your Python code a proper package")
        
        if "javascript" in analysis["languages"] or "typescript" in analysis["languages"]:
            if not any("package.json" in f for f in analysis["files"]):
                suggestions.append("Add package.json for Node.js project")
        
        return suggestions
    
    async def suggest_next_task(self, current_context: str = "") -> str:
        """Suggest the next task based on project analysis and goals"""
        if not self.current_session:
            return "❌ No active coding session. Start one with start_coding_session()"
        
        # Analyze current state
        project_analysis = await self.analyze_project_structure()
        
        # Generate task suggestion
        prompt = f"""
Based on the current project state and goals, suggest the next most important task.

Project: {self.current_session['description']}
Goals: {', '.join(self.current_session['goals'])}
Completed tasks: {', '.join(self.current_session['completed_tasks'])}

Current project analysis:
- Files: {len(project_analysis['files'])} files
- Languages: {', '.join(project_analysis['languages'])}
- Has tests: {project_analysis['structure']['has_tests']}
- Has docs: {project_analysis['structure']['has_docs']}

Current context: {current_context}

Suggest the next most important task with:
1. Task description
2. Why it's important
3. Estimated effort
4. Prerequisites
"""
        
        if self.llm_client:
            response = await self.llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            return response
        else:
            # Fallback suggestion based on analysis
            if not project_analysis['structure']['has_tests']:
                return "🧪 **Next Task**: Add unit tests\n\nWhy: Testing ensures code reliability and catches bugs early.\nEffort: Medium\nPrerequisites: Identify core functions to test"
            elif not project_analysis['structure']['has_docs']:
                return "📚 **Next Task**: Add documentation\n\nWhy: Good documentation helps team collaboration and maintenance.\nEffort: Low-Medium\nPrerequisites: Understand main features"
            else:
                return "🔧 **Next Task**: Code review and refactoring\n\nWhy: Improve code quality and maintainability.\nEffort: Medium\nPrerequisites: Identify areas for improvement"
    
    async def execute_workflow_step(self, step_type: str, **kwargs) -> str:
        """Execute a specific workflow step"""
        try:
            if step_type == "code_review":
                return await self.commands.code_review(**kwargs)
            elif step_type == "bug_analysis":
                return await self.commands.bug_analysis(**kwargs)
            elif step_type == "architecture_design":
                return await self.commands.architecture_design(**kwargs)
            elif step_type == "implement_feature":
                return await self.commands.implement_feature(**kwargs)
            elif step_type == "refactor_code":
                return await self.commands.refactor_code(**kwargs)
            elif step_type == "explain_concept":
                return await self.commands.explain_concept(**kwargs)
            elif step_type == "optimize_performance":
                return await self.commands.optimize_performance(**kwargs)
            else:
                return f"❌ Unknown workflow step: {step_type}"
                
        except Exception as e:
            return f"❌ Error executing workflow step {step_type}: {e}"
    
    async def complete_task(self, task_description: str, result: str) -> str:
        """Mark a task as completed"""
        if not self.current_session:
            return "❌ No active coding session"
        
        self.current_session["completed_tasks"].append({
            "description": task_description,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        console.print(f"✅ [green]Task completed:[/green] {task_description}")
        return f"✅ Task marked as completed: {task_description}"
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        if not self.current_session:
            return "❌ No active coding session"
        
        session = self.current_session
        completed_count = len(session["completed_tasks"])
        
        summary = f"""
**📊 Session Summary**

**Project:** {session['description']}
**Session ID:** {session['id']}
**Goals:** {len(session['goals'])} goals defined
**Completed Tasks:** {completed_count} tasks

**Goals:**
{chr(10).join(f"  • {goal}" for goal in session['goals'])}

**Completed Tasks:**
{chr(10).join(f"  ✅ {task['description']}" for task in session['completed_tasks'])}
"""
        
        return summary
    
    async def generate_session_report(self) -> str:
        """Generate comprehensive session report"""
        if not self.current_session:
            return "❌ No active coding session"
        
        # Basic session info
        summary = self.get_session_summary()
        
        # Project analysis
        project_analysis = await self.analyze_project_structure()
        
        # Generate insights
        insights_prompt = f"""
Generate insights and recommendations based on this coding session:

{summary}

Project Analysis:
- Files: {len(project_analysis['files'])}
- Languages: {', '.join(project_analysis['languages'])}
- Structure: {project_analysis['structure']}
- Suggestions: {project_analysis['suggestions']}

Provide:
1. Key achievements
2. Areas for improvement
3. Next steps
4. Technical recommendations
"""
        
        if self.llm_client:
            insights = await self.llm_client.achat_completion([
                {"role": "user", "content": insights_prompt}
            ])
            return f"{summary}\n\n**🔍 AI Insights:**\n{insights}"
        else:
            return summary
    
    def end_session(self) -> str:
        """End current coding session"""
        if not self.current_session:
            return "❌ No active coding session"
        
        # Save to history
        self.workflow_history.append(self.current_session.copy())
        
        session_id = self.current_session["id"]
        completed_tasks = len(self.current_session["completed_tasks"])
        
        # Clear current session
        self.current_session = {}
        
        console.print(Panel(
            f"[bold yellow]📋 Session Ended[/bold yellow]\n\n"
            f"[cyan]Session ID:[/cyan] {session_id}\n"
            f"[cyan]Tasks Completed:[/cyan] {completed_tasks}\n"
            f"[cyan]Session saved to history[/cyan]",
            title="✨ Vibecoding Session Complete",
            border_style="yellow"
        ))
        
        return f"✅ Session {session_id} ended. {completed_tasks} tasks completed."


# Global instance
vibecoding_workflow = VibecodingWorkflow()
