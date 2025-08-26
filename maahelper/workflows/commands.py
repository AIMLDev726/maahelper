"""
Workflow CLI Commands for MaaHelper
Commands for creating, managing, and monitoring project-wide workflows
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.llm_client import UnifiedLLMClient
from .engine import WorkflowEngine
from .templates import WorkflowTemplates
from .state import WorkflowStateManager

console = Console()

class WorkflowCommands:
    """CLI commands for workflow management"""
    
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None, 
                 workspace_path: str = "."):
        self.llm_client = llm_client
        self.workspace_path = workspace_path
        self.engine = WorkflowEngine(llm_client, workspace_path)
        self.templates = WorkflowTemplates()
        self.state_manager = WorkflowStateManager(workspace_path)
    
    async def list_templates(self, category: Optional[str] = None) -> str:
        """List available workflow templates"""
        templates = self.templates.list_templates(category)
        
        if not templates:
            return "❌ No workflow templates found"
        
        table = Table(title="📋 Available Workflow Templates")
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="green")
        table.add_column("Description", style="white")
        table.add_column("Tags", style="yellow")
        
        for template in templates:
            tags_str = ", ".join(template.tags)
            table.add_row(
                template.name,
                template.category,
                template.description[:60] + "..." if len(template.description) > 60 else template.description,
                tags_str
            )
        
        console.print(table)
        return f"✅ Found {len(templates)} workflow templates"
    
    async def create_workflow_from_template(self, template_name: str, 
                                          custom_inputs: Optional[Dict[str, Any]] = None) -> str:
        """Create a workflow from a template"""
        try:
            template = self.templates.get_template(template_name)
            
            console.print(Panel(
                f"[bold blue]Creating Workflow from Template[/bold blue]\n\n"
                f"[cyan]Template:[/cyan] {template.name}\n"
                f"[cyan]Category:[/cyan] {template.category}\n"
                f"[cyan]Description:[/cyan] {template.description}",
                title="🔄 Workflow Creation",
                border_style="blue"
            ))
            
            # Merge custom inputs with defaults
            inputs = {**template.default_inputs}
            if custom_inputs:
                inputs.update(custom_inputs)
            
            # Interactive input collection if needed
            if not custom_inputs:
                inputs = await self._collect_template_inputs(template, inputs)
            
            # Create workflow
            workflow_id = await self.engine.create_workflow(
                name=template.name,
                description=template.description,
                steps=template.steps,
                dependencies=template.dependencies
            )
            
            return f"✅ Workflow created with ID: {workflow_id}"
            
        except ValueError as e:
            return f"❌ Template error: {e}"
        except Exception as e:
            return f"❌ Failed to create workflow: {e}"
    
    async def create_custom_workflow(self, name: str, description: str, 
                                   steps_config: List[Dict[str, Any]]) -> str:
        """Create a custom workflow"""
        try:
            console.print(Panel(
                f"[bold green]Creating Custom Workflow[/bold green]\n\n"
                f"[cyan]Name:[/cyan] {name}\n"
                f"[cyan]Description:[/cyan] {description}\n"
                f"[cyan]Steps:[/cyan] {len(steps_config)}",
                title="🔧 Custom Workflow",
                border_style="green"
            ))
            
            workflow_id = await self.engine.create_workflow(
                name=name,
                description=description,
                steps=steps_config
            )
            
            return f"✅ Custom workflow created with ID: {workflow_id}"
            
        except Exception as e:
            return f"❌ Failed to create custom workflow: {e}"
    
    async def execute_workflow(self, workflow_id: str, 
                             context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a workflow"""
        try:
            console.print(f"[blue]🚀 Starting workflow execution: {workflow_id}[/blue]")
            
            success = await self.engine.execute_workflow(workflow_id, context)
            
            if success:
                return f"✅ Workflow {workflow_id} completed successfully!"
            else:
                return f"❌ Workflow {workflow_id} failed to complete"
                
        except Exception as e:
            return f"❌ Workflow execution error: {e}"
    
    async def list_workflows(self, status_filter: Optional[str] = None) -> str:
        """List all workflows"""
        try:
            # Get active workflows
            active_workflows = self.engine.list_active_workflows()
            
            # Get all workflows from state manager
            all_workflows = await self.state_manager.list_all_workflows()
            
            # Combine and filter
            workflows = []
            
            # Add active workflows
            for wf in active_workflows:
                workflows.append({
                    **wf,
                    'source': 'active'
                })
            
            # Add stored workflows that aren't active
            active_ids = {wf['id'] for wf in active_workflows}
            for wf in all_workflows:
                if wf['id'] not in active_ids:
                    workflows.append({
                        **wf,
                        'source': 'stored'
                    })
            
            # Apply status filter
            if status_filter:
                workflows = [wf for wf in workflows if wf.get('status') == status_filter]
            
            if not workflows:
                return "📭 No workflows found"
            
            table = Table(title="🔄 Workflows")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Progress", style="blue")
            table.add_column("Created", style="dim")
            
            for wf in workflows:
                progress_str = ""
                if 'progress_percentage' in wf:
                    progress_str = f"{wf['progress_percentage']:.1f}%"
                elif 'completed_steps' in wf and 'total_steps' in wf:
                    if wf['total_steps'] > 0:
                        progress = (wf['completed_steps'] / wf['total_steps']) * 100
                        progress_str = f"{progress:.1f}%"
                
                table.add_row(
                    wf['id'][:8] + "...",
                    wf.get('name', 'Unknown'),
                    wf.get('status', 'Unknown'),
                    progress_str,
                    wf.get('created_at', '')[:10] if wf.get('created_at') else ''
                )
            
            console.print(table)
            return f"✅ Found {len(workflows)} workflows"
            
        except Exception as e:
            return f"❌ Failed to list workflows: {e}"
    
    async def get_workflow_status(self, workflow_id: str) -> str:
        """Get detailed status of a workflow"""
        try:
            # Try to get from active workflows first
            status = self.engine.get_workflow_status(workflow_id)
            
            if not status:
                # Try to load from state manager
                state_data = await self.state_manager.load_workflow_state(workflow_id)
                if state_data:
                    status = {
                        'id': workflow_id,
                        'status': state_data.get('status', 'unknown'),
                        'completed_steps': len(state_data.get('completed_steps', [])),
                        'failed_steps': len(state_data.get('failed_steps', [])),
                        'total_steps': len(state_data.get('definition', {}).get('steps', []))
                    }
            
            if not status:
                return f"❌ Workflow {workflow_id} not found"
            
            console.print(Panel(
                f"[cyan]ID:[/cyan] {status['id']}\n"
                f"[cyan]Name:[/cyan] {status.get('name', 'Unknown')}\n"
                f"[cyan]Status:[/cyan] {status.get('status', 'Unknown')}\n"
                f"[cyan]Progress:[/cyan] {status.get('completed_steps', 0)}/{status.get('total_steps', 0)} steps\n"
                f"[cyan]Failed Steps:[/cyan] {status.get('failed_steps', 0)}\n"
                f"[cyan]Running Steps:[/cyan] {status.get('running_steps', 0)}",
                title="📊 Workflow Status",
                border_style="blue"
            ))
            
            return "✅ Workflow status retrieved"
            
        except Exception as e:
            return f"❌ Failed to get workflow status: {e}"
    
    async def pause_workflow(self, workflow_id: str) -> str:
        """Pause a running workflow"""
        try:
            success = await self.engine.pause_workflow(workflow_id)
            if success:
                return f"⏸️ Workflow {workflow_id} paused"
            else:
                return f"❌ Failed to pause workflow {workflow_id}"
        except Exception as e:
            return f"❌ Error pausing workflow: {e}"
    
    async def resume_workflow(self, workflow_id: str) -> str:
        """Resume a paused workflow"""
        try:
            success = await self.engine.resume_workflow(workflow_id)
            if success:
                return f"▶️ Workflow {workflow_id} resumed"
            else:
                return f"❌ Failed to resume workflow {workflow_id}"
        except Exception as e:
            return f"❌ Error resuming workflow: {e}"
    
    async def cancel_workflow(self, workflow_id: str) -> str:
        """Cancel a workflow"""
        try:
            success = await self.engine.cancel_workflow(workflow_id)
            if success:
                return f"❌ Workflow {workflow_id} cancelled"
            else:
                return f"❌ Failed to cancel workflow {workflow_id}"
        except Exception as e:
            return f"❌ Error cancelling workflow: {e}"
    
    async def create_checkpoint(self, workflow_id: str, checkpoint_name: str) -> str:
        """Create a checkpoint for a workflow"""
        try:
            # Get current workflow state
            status = self.engine.get_workflow_status(workflow_id)
            if not status:
                return f"❌ Workflow {workflow_id} not found"
            
            success = await self.state_manager.create_checkpoint(
                workflow_id, checkpoint_name, status
            )
            
            if success:
                return f"✅ Checkpoint '{checkpoint_name}' created for workflow {workflow_id}"
            else:
                return f"❌ Failed to create checkpoint"
                
        except Exception as e:
            return f"❌ Error creating checkpoint: {e}"
    
    async def list_checkpoints(self, workflow_id: str) -> str:
        """List checkpoints for a workflow"""
        try:
            checkpoints = await self.state_manager.list_checkpoints(workflow_id)
            
            if not checkpoints:
                return f"📭 No checkpoints found for workflow {workflow_id}"
            
            table = Table(title=f"📍 Checkpoints for {workflow_id[:8]}...")
            table.add_column("Name", style="cyan")
            table.add_column("Created", style="green")
            
            for checkpoint in checkpoints:
                table.add_row(
                    checkpoint['name'],
                    checkpoint['created_at'][:19] if checkpoint['created_at'] else ''
                )
            
            console.print(table)
            return f"✅ Found {len(checkpoints)} checkpoints"
            
        except Exception as e:
            return f"❌ Error listing checkpoints: {e}"
    
    async def restore_checkpoint(self, workflow_id: str, checkpoint_name: str) -> str:
        """Restore workflow from a checkpoint"""
        try:
            checkpoint_data = await self.state_manager.restore_from_checkpoint(
                workflow_id, checkpoint_name
            )
            
            if checkpoint_data:
                return f"✅ Workflow {workflow_id} restored from checkpoint '{checkpoint_name}'"
            else:
                return f"❌ Checkpoint '{checkpoint_name}' not found"
                
        except Exception as e:
            return f"❌ Error restoring checkpoint: {e}"
    
    async def get_workflow_statistics(self) -> str:
        """Get workflow statistics"""
        try:
            stats = await self.state_manager.get_workflow_statistics()
            
            console.print(Panel(
                f"[cyan]Total Workflows:[/cyan] {stats.get('total_workflows', 0)}\n"
                f"[cyan]Completed Steps:[/cyan] {stats.get('total_completed_steps', 0)}\n"
                f"[cyan]Failed Steps:[/cyan] {stats.get('total_failed_steps', 0)}\n\n"
                f"[yellow]By Status:[/yellow]\n" +
                "\n".join(f"  {status}: {count}" for status, count in stats.get('by_status', {}).items()),
                title="📈 Workflow Statistics",
                border_style="green"
            ))
            
            return "✅ Statistics retrieved"
            
        except Exception as e:
            return f"❌ Error getting statistics: {e}"
    
    async def cleanup_old_workflows(self, days_old: int = 30) -> str:
        """Clean up old completed workflows"""
        try:
            if not Confirm.ask(f"Clean up workflows older than {days_old} days?"):
                return "❌ Cleanup cancelled"
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Cleaning up old workflows...", total=None)
                
                cleaned_count = await self.state_manager.cleanup_old_workflows(days_old)
                
                progress.update(task, completed=True)
            
            return f"✅ Cleaned up {cleaned_count} old workflows"
            
        except Exception as e:
            return f"❌ Error during cleanup: {e}"
    
    async def _collect_template_inputs(self, template, default_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Interactively collect inputs for a template"""
        inputs = default_inputs.copy()
        
        console.print("\n[yellow]📝 Please provide the following inputs:[/yellow]")
        
        # Common inputs that might need user input
        input_prompts = {
            'feature_name': 'Feature name',
            'requirements': 'Feature requirements',
            'bug_description': 'Bug description',
            'project_name': 'Project name',
            'project_type': 'Project type (python/javascript/etc)',
            'license_type': 'License type (MIT/Apache/etc)',
            'target_language': 'Target programming language'
        }
        
        for key, prompt_text in input_prompts.items():
            if key in inputs and not inputs[key]:
                value = Prompt.ask(f"[cyan]{prompt_text}[/cyan]", default=inputs.get(key, ''))
                if value:
                    inputs[key] = value
        
        return inputs
