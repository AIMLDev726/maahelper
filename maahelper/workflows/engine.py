"""
Workflow Engine for MaaHelper
LangGraph-based workflow orchestration for complex coding tasks
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import uuid

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from ..core.llm_client import UnifiedLLMClient
from .state import WorkflowState, WorkflowStateManager
from .nodes import WorkflowNodes

console = Console()
logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    id: str
    name: str
    description: str
    node_type: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class WorkflowDefinition:
    """Defines a complete workflow"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    dependencies: Dict[str, List[str]]  # step_id -> [dependency_step_ids]
    metadata: Dict[str, Any]

class WorkflowEngine:
    """
    Core workflow engine using LangGraph-inspired architecture
    Orchestrates complex, multi-step coding tasks across projects
    """
    
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None, 
                 workspace_path: str = "."):
        self.llm_client = llm_client
        self.workspace_path = Path(workspace_path)
        self.state_manager = WorkflowStateManager(workspace_path)
        self.nodes = WorkflowNodes(llm_client)
        
        # Active workflows
        self.active_workflows: Dict[str, WorkflowDefinition] = {}
        self.workflow_progress: Dict[str, Progress] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            'workflow_started': [],
            'workflow_completed': [],
            'workflow_failed': [],
            'step_started': [],
            'step_completed': [],
            'step_failed': []
        }
    
    async def create_workflow(self, name: str, description: str, 
                            steps: List[Dict[str, Any]], 
                            dependencies: Optional[Dict[str, List[str]]] = None) -> str:
        """Create a new workflow definition"""
        workflow_id = str(uuid.uuid4())
        
        # Convert step dictionaries to WorkflowStep objects
        workflow_steps = []
        for i, step_data in enumerate(steps):
            step = WorkflowStep(
                id=step_data.get('id', f"step_{i}"),
                name=step_data['name'],
                description=step_data['description'],
                node_type=step_data['node_type'],
                inputs=step_data.get('inputs', {}),
                outputs={}
            )
            workflow_steps.append(step)
        
        workflow = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            steps=workflow_steps,
            dependencies=dependencies or {},
            metadata={
                'created_at': datetime.now().isoformat(),
                'workspace': str(self.workspace_path)
            }
        )
        
        self.active_workflows[workflow_id] = workflow
        
        # Save workflow state
        await self.state_manager.save_workflow_state(workflow_id, {
            'definition': asdict(workflow),
            'status': 'created'
        })
        
        console.print(Panel(
            f"[bold green]✅ Workflow Created[/bold green]\n\n"
            f"[cyan]ID:[/cyan] {workflow_id}\n"
            f"[cyan]Name:[/cyan] {name}\n"
            f"[cyan]Steps:[/cyan] {len(workflow_steps)}\n"
            f"[cyan]Description:[/cyan] {description}",
            title="🔄 New Workflow",
            border_style="green"
        ))
        
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str, 
                             initial_context: Optional[Dict[str, Any]] = None) -> bool:
        """Execute a workflow with dependency resolution"""
        if workflow_id not in self.active_workflows:
            console.print(f"[red]❌ Workflow {workflow_id} not found[/red]")
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        console.print(Panel(
            f"[bold blue]🚀 Starting Workflow Execution[/bold blue]\n\n"
            f"[cyan]Name:[/cyan] {workflow.name}\n"
            f"[cyan]Steps:[/cyan] {len(workflow.steps)}\n"
            f"[cyan]Description:[/cyan] {workflow.description}",
            title="🔄 Workflow Execution",
            border_style="blue"
        ))
        
        # Initialize progress tracking
        progress = Progress()
        self.workflow_progress[workflow_id] = progress
        
        try:
            # Fire workflow started event
            await self._fire_event('workflow_started', workflow_id, workflow)
            
            # Initialize workflow context
            context = initial_context or {}
            context['workspace_path'] = str(self.workspace_path)
            context['workflow_id'] = workflow_id
            
            # Execute steps in dependency order
            success = await self._execute_workflow_steps(workflow, context, progress)
            
            if success:
                await self._fire_event('workflow_completed', workflow_id, workflow)
                console.print(f"[bold green]✅ Workflow '{workflow.name}' completed successfully![/bold green]")
            else:
                await self._fire_event('workflow_failed', workflow_id, workflow)
                console.print(f"[bold red]❌ Workflow '{workflow.name}' failed![/bold red]")
            
            return success
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            await self._fire_event('workflow_failed', workflow_id, workflow)
            console.print(f"[bold red]❌ Workflow execution failed: {e}[/bold red]")
            return False
        
        finally:
            # Cleanup progress tracking
            if workflow_id in self.workflow_progress:
                del self.workflow_progress[workflow_id]
    
    async def _execute_workflow_steps(self, workflow: WorkflowDefinition, 
                                    context: Dict[str, Any], progress: Progress) -> bool:
        """Execute workflow steps in dependency order"""
        # Create dependency graph
        completed_steps = set()
        failed_steps = set()
        
        # Add progress tasks
        step_tasks = {}
        with progress:
            for step in workflow.steps:
                task_id = progress.add_task(f"[cyan]{step.name}[/cyan]", total=1)
                step_tasks[step.id] = task_id
            
            progress.start()
            
            # Execute steps
            while len(completed_steps) + len(failed_steps) < len(workflow.steps):
                # Find steps ready to execute
                ready_steps = []
                for step in workflow.steps:
                    if (step.id not in completed_steps and 
                        step.id not in failed_steps and
                        step.status == "pending"):
                        
                        # Check if all dependencies are completed
                        dependencies = workflow.dependencies.get(step.id, [])
                        if all(dep_id in completed_steps for dep_id in dependencies):
                            ready_steps.append(step)
                
                if not ready_steps:
                    # Check if we're stuck due to failed dependencies
                    remaining_steps = [s for s in workflow.steps 
                                     if s.id not in completed_steps and s.id not in failed_steps]
                    if remaining_steps:
                        console.print("[red]❌ Workflow stuck - dependency deadlock detected[/red]")
                        return False
                    break
                
                # Execute ready steps (can be done in parallel)
                tasks = []
                for step in ready_steps:
                    task = self._execute_step(step, context, workflow_id, step_tasks[step.id], progress)
                    tasks.append(task)
                
                # Wait for all ready steps to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(results):
                    step = ready_steps[i]
                    if isinstance(result, Exception):
                        step.status = "failed"
                        step.error = str(result)
                        failed_steps.add(step.id)
                        console.print(f"[red]❌ Step '{step.name}' failed: {result}[/red]")
                    elif result:
                        step.status = "completed"
                        completed_steps.add(step.id)
                        progress.update(step_tasks[step.id], completed=1)
                    else:
                        step.status = "failed"
                        failed_steps.add(step.id)
                        console.print(f"[red]❌ Step '{step.name}' failed[/red]")
                
                # Update workflow state
                await self.state_manager.save_workflow_state(workflow.id, {
                    'definition': asdict(workflow),
                    'status': 'running',
                    'completed_steps': list(completed_steps),
                    'failed_steps': list(failed_steps),
                    'context': context
                })
        
        # Check if all steps completed successfully
        return len(failed_steps) == 0 and len(completed_steps) == len(workflow.steps)
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any],
                          workflow_id: str, task_id: int, progress: Progress) -> bool:
        """Execute a single workflow step"""
        try:
            step.status = "running"
            step.started_at = datetime.now()
            
            await self._fire_event('step_started', workflow_id, step)
            
            # Prepare step inputs with context
            step_inputs = {**context, **step.inputs}
            
            # Execute the step using the appropriate node
            result = await self.nodes.execute_node(step.node_type, step_inputs)
            
            if result:
                step.outputs = result
                step.status = "completed"
                step.completed_at = datetime.now()
                
                # Update context with step outputs
                context.update(result)
                
                await self._fire_event('step_completed', workflow_id, step)
                return True
            else:
                step.status = "failed"
                step.error = "Node execution returned no result"
                await self._fire_event('step_failed', workflow_id, step)
                return False
                
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now()
            await self._fire_event('step_failed', workflow_id, step)
            logger.error(f"Step execution error: {e}")
            return False
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        # Save current state
        workflow = self.active_workflows[workflow_id]
        await self.state_manager.save_workflow_state(workflow_id, {
            'definition': asdict(workflow),
            'status': 'paused'
        })
        
        console.print(f"[yellow]⏸️ Workflow '{workflow.name}' paused[/yellow]")
        return True
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        if workflow_id not in self.active_workflows:
            # Try to load from state
            state = await self.state_manager.load_workflow_state(workflow_id)
            if state:
                workflow_data = state['definition']
                workflow = WorkflowDefinition(**workflow_data)
                self.active_workflows[workflow_id] = workflow
            else:
                return False
        
        workflow = self.active_workflows[workflow_id]
        console.print(f"[green]▶️ Resuming workflow '{workflow.name}'[/green]")
        
        # Continue execution from where it left off
        return await self.execute_workflow(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        if workflow_id not in self.active_workflows:
            return False
        
        workflow = self.active_workflows[workflow_id]
        
        # Update state
        await self.state_manager.save_workflow_state(workflow_id, {
            'definition': asdict(workflow),
            'status': 'cancelled'
        })
        
        # Remove from active workflows
        del self.active_workflows[workflow_id]
        
        console.print(f"[red]❌ Workflow '{workflow.name}' cancelled[/red]")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        if workflow_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[workflow_id]
        
        completed_steps = sum(1 for step in workflow.steps if step.status == "completed")
        failed_steps = sum(1 for step in workflow.steps if step.status == "failed")
        running_steps = sum(1 for step in workflow.steps if step.status == "running")
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'total_steps': len(workflow.steps),
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'running_steps': running_steps,
            'progress_percentage': (completed_steps / len(workflow.steps)) * 100 if workflow.steps else 0
        }
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows"""
        return [self.get_workflow_status(wf_id) for wf_id in self.active_workflows.keys()]
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
    
    async def _fire_event(self, event_type: str, workflow_id: str, data: Any):
        """Fire an event to all registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(workflow_id, data)
                    else:
                        handler(workflow_id, data)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
