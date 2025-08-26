#!/usr/bin/env python3
"""
Git Integration & Smart Commits
AI-assisted Git operations with smart commit messages and branch suggestions
"""

import asyncio
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()


@dataclass
class GitChange:
    """Represents a Git change"""
    file_path: str
    change_type: str  # "added", "modified", "deleted", "renamed"
    lines_added: int = 0
    lines_removed: int = 0
    is_binary: bool = False


@dataclass
class CommitSuggestion:
    """AI-generated commit message suggestion"""
    type: str  # "feat", "fix", "docs", "style", "refactor", "test", "chore"
    scope: str
    description: str
    body: str = ""
    breaking_change: bool = False
    confidence: float = 0.0


class GitAnalyzer:
    """Analyzes Git changes and generates intelligent suggestions"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.commit_patterns = self._initialize_commit_patterns()
    
    def _initialize_commit_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for commit type detection"""
        return {
            "feat": [
                r"add.*feature", r"implement.*", r"create.*", r"new.*functionality",
                r"introduce.*", r"support.*", r"enable.*"
            ],
            "fix": [
                r"fix.*bug", r"resolve.*", r"correct.*", r"repair.*",
                r"patch.*", r"address.*issue", r"solve.*"
            ],
            "docs": [
                r"update.*documentation", r"add.*docs", r"improve.*readme",
                r"document.*", r"comment.*", r"explain.*"
            ],
            "style": [
                r"format.*", r"style.*", r"lint.*", r"prettier.*",
                r"whitespace.*", r"indentation.*", r"cleanup.*"
            ],
            "refactor": [
                r"refactor.*", r"restructure.*", r"reorganize.*",
                r"simplify.*", r"optimize.*", r"improve.*structure"
            ],
            "test": [
                r"add.*test", r"test.*", r"spec.*", r"coverage.*",
                r"unit.*test", r"integration.*test"
            ],
            "chore": [
                r"update.*dependencies", r"bump.*version", r"config.*",
                r"build.*", r"ci.*", r"maintenance.*"
            ]
        }
    
    async def get_git_status(self) -> List[GitChange]:
        """Get current Git status"""
        try:
            # Get staged changes
            result = await self._run_git_command(["diff", "--cached", "--name-status"])
            staged_changes = self._parse_git_status(result)
            
            # Get unstaged changes
            result = await self._run_git_command(["diff", "--name-status"])
            unstaged_changes = self._parse_git_status(result)
            
            # Combine and get detailed info
            all_changes = staged_changes + unstaged_changes
            detailed_changes = []
            
            for change in all_changes:
                detailed_change = await self._get_change_details(change)
                detailed_changes.append(detailed_change)
            
            return detailed_changes
            
        except Exception as e:
            console.print(f"[red]Error getting Git status: {e}[/red]")
            return []
    
    def _parse_git_status(self, status_output: str) -> List[GitChange]:
        """Parse Git status output"""
        changes = []
        for line in status_output.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2:
                status = parts[0]
                file_path = parts[1]
                
                change_type = "modified"
                if status.startswith('A'):
                    change_type = "added"
                elif status.startswith('D'):
                    change_type = "deleted"
                elif status.startswith('R'):
                    change_type = "renamed"
                elif status.startswith('M'):
                    change_type = "modified"
                
                changes.append(GitChange(
                    file_path=file_path,
                    change_type=change_type
                ))
        
        return changes
    
    async def _get_change_details(self, change: GitChange) -> GitChange:
        """Get detailed information about a change"""
        try:
            if change.change_type != "deleted":
                # Get diff stats
                result = await self._run_git_command([
                    "diff", "--numstat", "HEAD", "--", change.file_path
                ])
                
                if result.strip():
                    parts = result.strip().split('\t')
                    if len(parts) >= 2:
                        try:
                            change.lines_added = int(parts[0]) if parts[0] != '-' else 0
                            change.lines_removed = int(parts[1]) if parts[1] != '-' else 0
                        except ValueError:
                            change.is_binary = True
            
            return change
            
        except Exception:
            return change
    
    async def generate_commit_message(self, changes: List[GitChange], llm_client=None) -> CommitSuggestion:
        """Generate intelligent commit message"""
        if not changes:
            return CommitSuggestion("chore", "", "Empty commit")
        
        # Analyze changes to determine commit type and scope
        commit_type, scope = self._analyze_commit_type(changes)
        
        # Generate description based on changes
        description = self._generate_description(changes, commit_type)
        
        # Use LLM for better suggestions if available
        if llm_client:
            enhanced_suggestion = await self._enhance_with_llm(changes, llm_client)
            if enhanced_suggestion:
                return enhanced_suggestion
        
        return CommitSuggestion(
            type=commit_type,
            scope=scope,
            description=description,
            confidence=0.7
        )
    
    def _analyze_commit_type(self, changes: List[GitChange]) -> Tuple[str, str]:
        """Analyze changes to determine commit type and scope"""
        file_paths = [change.file_path for change in changes]
        
        # Determine scope based on file paths
        scope = self._determine_scope(file_paths)
        
        # Determine type based on file patterns and changes
        if any("test" in path.lower() for path in file_paths):
            return "test", scope
        
        if any(path.endswith(('.md', '.txt', '.rst')) for path in file_paths):
            return "docs", scope
        
        if any(change.change_type == "added" for change in changes):
            return "feat", scope
        
        if any("fix" in path.lower() or "bug" in path.lower() for path in file_paths):
            return "fix", scope
        
        if all(change.lines_added + change.lines_removed < 10 for change in changes):
            return "style", scope
        
        return "feat", scope
    
    def _determine_scope(self, file_paths: List[str]) -> str:
        """Determine scope based on file paths"""
        # Group files by directory
        directories = set()
        for path in file_paths:
            parts = Path(path).parts
            if len(parts) > 1:
                directories.add(parts[0])
        
        if len(directories) == 1:
            return list(directories)[0]
        elif len(directories) <= 3:
            return "/".join(sorted(directories))
        else:
            return "multiple"
    
    def _generate_description(self, changes: List[GitChange], commit_type: str) -> str:
        """Generate commit description"""
        if len(changes) == 1:
            change = changes[0]
            file_name = Path(change.file_path).name
            
            if change.change_type == "added":
                return f"add {file_name}"
            elif change.change_type == "deleted":
                return f"remove {file_name}"
            elif change.change_type == "modified":
                return f"update {file_name}"
            elif change.change_type == "renamed":
                return f"rename {file_name}"
        
        # Multiple files
        added = len([c for c in changes if c.change_type == "added"])
        modified = len([c for c in changes if c.change_type == "modified"])
        deleted = len([c for c in changes if c.change_type == "deleted"])
        
        parts = []
        if added:
            parts.append(f"add {added} file{'s' if added > 1 else ''}")
        if modified:
            parts.append(f"update {modified} file{'s' if modified > 1 else ''}")
        if deleted:
            parts.append(f"remove {deleted} file{'s' if deleted > 1 else ''}")
        
        return " and ".join(parts)
    
    async def _enhance_with_llm(self, changes: List[GitChange], llm_client) -> Optional[CommitSuggestion]:
        """Enhance commit message using LLM"""
        try:
            # Get actual diff content for context
            diff_content = await self._get_diff_content(changes[:5])  # Limit to 5 files
            
            prompt = f"""
Analyze the following Git changes and generate a conventional commit message.

Changes:
{self._format_changes_for_llm(changes)}

Diff content (first 1000 chars):
{diff_content[:1000]}

Generate a commit message following conventional commits format:
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Keep description under 50 characters.
Focus on WHAT changed, not HOW.

Respond with just the commit message.
"""
            
            response = await llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            # Parse the response
            return self._parse_llm_response(response)
            
        except Exception as e:
            console.print(f"[yellow]Could not enhance with LLM: {e}[/yellow]")
            return None
    
    def _format_changes_for_llm(self, changes: List[GitChange]) -> str:
        """Format changes for LLM prompt"""
        formatted = []
        for change in changes:
            formatted.append(f"- {change.change_type}: {change.file_path}")
            if change.lines_added or change.lines_removed:
                formatted.append(f"  (+{change.lines_added}, -{change.lines_removed})")
        return "\n".join(formatted)
    
    async def _get_diff_content(self, changes: List[GitChange]) -> str:
        """Get diff content for changes"""
        try:
            file_paths = [change.file_path for change in changes if change.change_type != "deleted"]
            if not file_paths:
                return ""
            
            result = await self._run_git_command(["diff", "HEAD", "--"] + file_paths)
            return result
            
        except Exception:
            return ""
    
    def _parse_llm_response(self, response: str) -> Optional[CommitSuggestion]:
        """Parse LLM response into CommitSuggestion"""
        try:
            # Extract conventional commit format
            match = re.match(r'(\w+)(?:\(([^)]+)\))?: (.+)', response.strip())
            if match:
                commit_type, scope, description = match.groups()
                return CommitSuggestion(
                    type=commit_type,
                    scope=scope or "",
                    description=description,
                    confidence=0.9
                )
        except Exception:
            pass
        
        return None
    
    async def suggest_branch_name(self, description: str) -> str:
        """Suggest branch name based on description"""
        # Clean and format description
        clean_desc = re.sub(r'[^\w\s-]', '', description.lower())
        clean_desc = re.sub(r'\s+', '-', clean_desc.strip())
        
        # Get current branch to determine prefix
        try:
            current_branch = await self._run_git_command(["branch", "--show-current"])
            current_branch = current_branch.strip()
            
            if current_branch.startswith(('feature/', 'feat/')):
                prefix = "feature/"
            elif current_branch.startswith(('fix/', 'bugfix/')):
                prefix = "fix/"
            elif current_branch.startswith(('hotfix/')):
                prefix = "hotfix/"
            else:
                prefix = "feature/"
        except:
            prefix = "feature/"
        
        return f"{prefix}{clean_desc[:40]}"
    
    async def _run_git_command(self, args: List[str]) -> str:
        """Run Git command and return output"""
        try:
            process = await asyncio.create_subprocess_exec(
                "git", *args,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Git command failed: {stderr.decode()}")
            
            return stdout.decode()
            
        except Exception as e:
            raise Exception(f"Failed to run git command: {e}")


class GitIntegration:
    """Main Git integration class"""
    
    def __init__(self, repo_path: str = "."):
        self.analyzer = GitAnalyzer(repo_path)
        self.repo_path = Path(repo_path)
    
    async def smart_commit(self, llm_client=None, auto_stage: bool = False) -> bool:
        """Perform smart commit with AI-generated message"""
        try:
            # Get current changes
            changes = await self.analyzer.get_git_status()
            
            if not changes:
                console.print("[yellow]No changes to commit[/yellow]")
                return False
            
            # Show changes
            self._display_changes(changes)
            
            # Auto-stage if requested
            if auto_stage:
                await self._stage_all_changes()
                console.print("✅ [green]Staged all changes[/green]")
            
            # Generate commit message
            console.print("🤖 [cyan]Generating commit message...[/cyan]")
            suggestion = await self.analyzer.generate_commit_message(changes, llm_client)
            
            # Format commit message
            commit_msg = self._format_commit_message(suggestion)
            
            # Show suggestion and confirm
            console.print(Panel(commit_msg, title="📝 Suggested Commit Message", border_style="green"))
            
            if Confirm.ask("Use this commit message?"):
                # Perform commit
                await self._commit_with_message(commit_msg)
                console.print("✅ [green]Commit successful![/green]")
                return True
            else:
                # Allow manual editing
                custom_msg = Prompt.ask("Enter custom commit message")
                if custom_msg:
                    await self._commit_with_message(custom_msg)
                    console.print("✅ [green]Commit successful![/green]")
                    return True
            
            return False
            
        except Exception as e:
            console.print(f"[red]Error during smart commit: {e}[/red]")
            return False
    
    def _display_changes(self, changes: List[GitChange]):
        """Display changes in a table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Changes", style="green")
        
        for change in changes:
            change_info = ""
            if change.lines_added or change.lines_removed:
                change_info = f"+{change.lines_added} -{change.lines_removed}"
            elif change.is_binary:
                change_info = "binary"
            
            table.add_row(
                change.file_path,
                change.change_type,
                change_info
            )
        
        console.print(Panel(table, title="📋 Git Changes", border_style="blue"))
    
    def _format_commit_message(self, suggestion: CommitSuggestion) -> str:
        """Format commit message from suggestion"""
        scope_part = f"({suggestion.scope})" if suggestion.scope else ""
        message = f"{suggestion.type}{scope_part}: {suggestion.description}"
        
        if suggestion.body:
            message += f"\n\n{suggestion.body}"
        
        if suggestion.breaking_change:
            message += "\n\nBREAKING CHANGE: This commit introduces breaking changes"
        
        return message
    
    async def _stage_all_changes(self):
        """Stage all changes"""
        await self.analyzer._run_git_command(["add", "."])
    
    async def _commit_with_message(self, message: str):
        """Commit with the given message"""
        await self.analyzer._run_git_command(["commit", "-m", message])
    
    async def suggest_branch_name_interactive(self) -> Optional[str]:
        """Interactive branch name suggestion"""
        description = Prompt.ask("Describe what you're working on")
        if description:
            suggestion = await self.analyzer.suggest_branch_name(description)
            console.print(f"💡 [cyan]Suggested branch name: {suggestion}[/cyan]")
            
            if Confirm.ask("Create this branch?"):
                try:
                    await self.analyzer._run_git_command(["checkout", "-b", suggestion])
                    console.print(f"✅ [green]Created and switched to branch: {suggestion}[/green]")
                    return suggestion
                except Exception as e:
                    console.print(f"[red]Error creating branch: {e}[/red]")
        
        return None
    
    async def generate_pr_description(self, llm_client=None) -> str:
        """Generate PR description based on recent commits"""
        try:
            # Get recent commits
            commits = await self.analyzer._run_git_command([
                "log", "--oneline", "-10", "HEAD"
            ])
            
            if not llm_client:
                return f"## Changes\n\n{commits}"
            
            prompt = f"""
Generate a pull request description based on these recent commits:

{commits}

Include:
- Brief summary of changes
- Key features or fixes
- Any breaking changes
- Testing notes if applicable

Format in Markdown.
"""
            
            response = await llm_client.achat_completion([
                {"role": "user", "content": prompt}
            ])
            
            return response
            
        except Exception as e:
            console.print(f"[red]Error generating PR description: {e}[/red]")
            return "## Changes\n\nPlease describe your changes here."


# Global instance
git_integration = GitIntegration()
