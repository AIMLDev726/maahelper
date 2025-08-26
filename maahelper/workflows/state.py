"""
Workflow State Management for MaaHelper
Handles persistent state for long-running workflows with checkpoints and resume capabilities
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class WorkflowState:
    """Represents the state of a workflow at a point in time"""
    workflow_id: str
    status: str  # created, running, paused, completed, failed, cancelled
    current_step: Optional[str] = None
    completed_steps: List[str] = None
    failed_steps: List[str] = None
    context: Dict[str, Any] = None
    checkpoints: List[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []
        if self.failed_steps is None:
            self.failed_steps = []
        if self.context is None:
            self.context = {}
        if self.checkpoints is None:
            self.checkpoints = []
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()

class WorkflowStateManager:
    """
    Manages persistent state for workflows with checkpoints and resume capabilities
    """
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.state_dir = self.workspace_path / ".maahelper" / "workflows"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for active workflow states
        self.state_cache: Dict[str, WorkflowState] = {}
        
        # Lock for concurrent access
        self._lock = asyncio.Lock()
    
    async def save_workflow_state(self, workflow_id: str, state_data: Dict[str, Any]) -> bool:
        """Save workflow state to persistent storage"""
        async with self._lock:
            try:
                # Create or update workflow state
                if workflow_id in self.state_cache:
                    state = self.state_cache[workflow_id]
                    # Update existing state
                    for key, value in state_data.items():
                        if hasattr(state, key):
                            setattr(state, key, value)
                    state.updated_at = datetime.now()
                else:
                    # Create new state
                    state = WorkflowState(
                        workflow_id=workflow_id,
                        **state_data
                    )
                    self.state_cache[workflow_id] = state
                
                # Save to file
                state_file = self.state_dir / f"{workflow_id}.json"
                state_dict = asdict(state)
                
                # Convert datetime objects to ISO strings
                if state_dict.get('created_at'):
                    state_dict['created_at'] = state.created_at.isoformat()
                if state_dict.get('updated_at'):
                    state_dict['updated_at'] = state.updated_at.isoformat()
                
                async with aiofiles.open(state_file, 'w') as f:
                    await f.write(json.dumps(state_dict, indent=2))
                
                logger.info(f"Saved workflow state for {workflow_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save workflow state for {workflow_id}: {e}")
                return False
    
    async def load_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from persistent storage"""
        async with self._lock:
            try:
                # Check cache first
                if workflow_id in self.state_cache:
                    return asdict(self.state_cache[workflow_id])
                
                # Load from file
                state_file = self.state_dir / f"{workflow_id}.json"
                if not state_file.exists():
                    return None
                
                async with aiofiles.open(state_file, 'r') as f:
                    content = await f.read()
                    state_dict = json.loads(content)
                
                # Convert ISO strings back to datetime objects
                if state_dict.get('created_at'):
                    state_dict['created_at'] = datetime.fromisoformat(state_dict['created_at'])
                if state_dict.get('updated_at'):
                    state_dict['updated_at'] = datetime.fromisoformat(state_dict['updated_at'])
                
                # Create state object and cache it
                state = WorkflowState(**state_dict)
                self.state_cache[workflow_id] = state
                
                logger.info(f"Loaded workflow state for {workflow_id}")
                return asdict(state)
                
            except Exception as e:
                logger.error(f"Failed to load workflow state for {workflow_id}: {e}")
                return None
    
    async def create_checkpoint(self, workflow_id: str, checkpoint_name: str, 
                              checkpoint_data: Dict[str, Any]) -> bool:
        """Create a checkpoint for a workflow"""
        async with self._lock:
            try:
                state = self.state_cache.get(workflow_id)
                if not state:
                    # Try to load from file
                    state_data = await self.load_workflow_state(workflow_id)
                    if not state_data:
                        return False
                    state = self.state_cache[workflow_id]
                
                # Add checkpoint
                checkpoint = {
                    'name': checkpoint_name,
                    'created_at': datetime.now().isoformat(),
                    'data': checkpoint_data
                }
                
                state.checkpoints.append(checkpoint)
                state.updated_at = datetime.now()
                
                # Save updated state
                return await self.save_workflow_state(workflow_id, asdict(state))
                
            except Exception as e:
                logger.error(f"Failed to create checkpoint for {workflow_id}: {e}")
                return False
    
    async def restore_from_checkpoint(self, workflow_id: str, 
                                    checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """Restore workflow state from a specific checkpoint"""
        async with self._lock:
            try:
                state_data = await self.load_workflow_state(workflow_id)
                if not state_data:
                    return None
                
                # Find the checkpoint
                checkpoints = state_data.get('checkpoints', [])
                for checkpoint in checkpoints:
                    if checkpoint['name'] == checkpoint_name:
                        logger.info(f"Restored workflow {workflow_id} from checkpoint {checkpoint_name}")
                        return checkpoint['data']
                
                logger.warning(f"Checkpoint {checkpoint_name} not found for workflow {workflow_id}")
                return None
                
            except Exception as e:
                logger.error(f"Failed to restore from checkpoint for {workflow_id}: {e}")
                return None
    
    async def list_checkpoints(self, workflow_id: str) -> List[Dict[str, Any]]:
        """List all checkpoints for a workflow"""
        try:
            state_data = await self.load_workflow_state(workflow_id)
            if not state_data:
                return []
            
            checkpoints = state_data.get('checkpoints', [])
            return [
                {
                    'name': cp['name'],
                    'created_at': cp['created_at']
                }
                for cp in checkpoints
            ]
            
        except Exception as e:
            logger.error(f"Failed to list checkpoints for {workflow_id}: {e}")
            return []
    
    async def delete_workflow_state(self, workflow_id: str) -> bool:
        """Delete workflow state and all associated data"""
        async with self._lock:
            try:
                # Remove from cache
                if workflow_id in self.state_cache:
                    del self.state_cache[workflow_id]
                
                # Remove file
                state_file = self.state_dir / f"{workflow_id}.json"
                if state_file.exists():
                    state_file.unlink()
                
                logger.info(f"Deleted workflow state for {workflow_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete workflow state for {workflow_id}: {e}")
                return False
    
    async def list_all_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with their basic information"""
        try:
            workflows = []
            
            # Scan state directory for workflow files
            for state_file in self.state_dir.glob("*.json"):
                workflow_id = state_file.stem
                
                try:
                    async with aiofiles.open(state_file, 'r') as f:
                        content = await f.read()
                        state_dict = json.loads(content)
                    
                    workflows.append({
                        'id': workflow_id,
                        'status': state_dict.get('status', 'unknown'),
                        'created_at': state_dict.get('created_at'),
                        'updated_at': state_dict.get('updated_at'),
                        'completed_steps': len(state_dict.get('completed_steps', [])),
                        'failed_steps': len(state_dict.get('failed_steps', []))
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to read workflow state file {state_file}: {e}")
                    continue
            
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    async def cleanup_old_workflows(self, days_old: int = 30) -> int:
        """Clean up workflow states older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            for state_file in self.state_dir.glob("*.json"):
                try:
                    # Check file modification time
                    if state_file.stat().st_mtime < cutoff_date:
                        # Load state to check if it's completed or failed
                        async with aiofiles.open(state_file, 'r') as f:
                            content = await f.read()
                            state_dict = json.loads(content)
                        
                        status = state_dict.get('status', '')
                        if status in ['completed', 'failed', 'cancelled']:
                            workflow_id = state_file.stem
                            await self.delete_workflow_state(workflow_id)
                            cleaned_count += 1
                            
                except Exception as e:
                    logger.warning(f"Failed to process workflow state file {state_file}: {e}")
                    continue
            
            logger.info(f"Cleaned up {cleaned_count} old workflow states")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old workflows: {e}")
            return 0
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about all workflows"""
        try:
            workflows = await self.list_all_workflows()
            
            stats = {
                'total_workflows': len(workflows),
                'by_status': {},
                'total_completed_steps': 0,
                'total_failed_steps': 0
            }
            
            for workflow in workflows:
                status = workflow['status']
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                stats['total_completed_steps'] += workflow['completed_steps']
                stats['total_failed_steps'] += workflow['failed_steps']
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            return {}
