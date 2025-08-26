"""
Tests for MaaHelper Workflow System
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from maahelper.workflows.engine import WorkflowEngine, WorkflowDefinition, WorkflowStep
from maahelper.workflows.templates import WorkflowTemplates
from maahelper.workflows.state import WorkflowStateManager
from maahelper.workflows.nodes import WorkflowNodes
from maahelper.workflows.commands import WorkflowCommands


class TestWorkflowEngine:
    """Test the workflow engine functionality"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="Test response")
        return client
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def workflow_engine(self, mock_llm_client, temp_workspace):
        """Workflow engine instance for testing"""
        return WorkflowEngine(mock_llm_client, temp_workspace)
    
    @pytest.mark.asyncio
    async def test_create_workflow(self, workflow_engine):
        """Test workflow creation"""
        steps = [
            {
                "name": "Test Step",
                "description": "A test step",
                "node_type": "log_message",
                "inputs": {"message": "Hello World"}
            }
        ]
        
        workflow_id = await workflow_engine.create_workflow(
            name="Test Workflow",
            description="A test workflow",
            steps=steps
        )
        
        assert workflow_id is not None
        assert workflow_id in workflow_engine.active_workflows
        
        workflow = workflow_engine.active_workflows[workflow_id]
        assert workflow.name == "Test Workflow"
        assert len(workflow.steps) == 1
    
    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, workflow_engine):
        """Test executing a simple workflow"""
        steps = [
            {
                "name": "Log Message",
                "description": "Log a test message",
                "node_type": "log_message",
                "inputs": {"message": "Test execution", "level": "info"}
            }
        ]
        
        workflow_id = await workflow_engine.create_workflow(
            name="Simple Test",
            description="Simple test workflow",
            steps=steps
        )
        
        success = await workflow_engine.execute_workflow(workflow_id)
        assert success is True
        
        # Check workflow status
        status = workflow_engine.get_workflow_status(workflow_id)
        assert status is not None
        assert status['completed_steps'] == 1
    
    @pytest.mark.asyncio
    async def test_workflow_with_dependencies(self, workflow_engine):
        """Test workflow with step dependencies"""
        steps = [
            {
                "id": "step1",
                "name": "First Step",
                "description": "First step",
                "node_type": "log_message",
                "inputs": {"message": "Step 1"}
            },
            {
                "id": "step2", 
                "name": "Second Step",
                "description": "Second step",
                "node_type": "log_message",
                "inputs": {"message": "Step 2"}
            }
        ]
        
        dependencies = {"step2": ["step1"]}
        
        workflow_id = await workflow_engine.create_workflow(
            name="Dependency Test",
            description="Test workflow dependencies",
            steps=steps,
            dependencies=dependencies
        )
        
        success = await workflow_engine.execute_workflow(workflow_id)
        assert success is True


class TestWorkflowTemplates:
    """Test workflow templates"""
    
    @pytest.fixture
    def templates(self):
        """Workflow templates instance"""
        return WorkflowTemplates()
    
    def test_list_templates(self, templates):
        """Test listing workflow templates"""
        all_templates = templates.list_templates()
        assert len(all_templates) > 0
        
        # Check specific templates exist
        template_names = [t.name for t in all_templates]
        assert "Code Quality Audit" in template_names
        assert "Feature Implementation" in template_names
    
    def test_get_template(self, templates):
        """Test getting specific template"""
        template = templates.get_template("code_quality_audit")
        assert template is not None
        assert template.name == "Code Quality Audit"
        assert len(template.steps) > 0
        assert template.category == "code_quality"
    
    def test_filter_by_category(self, templates):
        """Test filtering templates by category"""
        testing_templates = templates.list_templates(category="testing")
        assert len(testing_templates) > 0
        
        for template in testing_templates:
            assert template.category == "testing"
    
    def test_get_categories(self, templates):
        """Test getting all categories"""
        categories = templates.get_categories()
        assert len(categories) > 0
        assert "code_quality" in categories
        assert "testing" in categories
        assert "documentation" in categories


class TestWorkflowStateManager:
    """Test workflow state management"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_workspace):
        """State manager instance"""
        return WorkflowStateManager(temp_workspace)
    
    @pytest.mark.asyncio
    async def test_save_and_load_state(self, state_manager):
        """Test saving and loading workflow state"""
        workflow_id = "test-workflow-123"
        state_data = {
            "status": "running",
            "completed_steps": ["step1"],
            "failed_steps": [],
            "context": {"test": "data"}
        }
        
        # Save state
        success = await state_manager.save_workflow_state(workflow_id, state_data)
        assert success is True
        
        # Load state
        loaded_state = await state_manager.load_workflow_state(workflow_id)
        assert loaded_state is not None
        assert loaded_state["status"] == "running"
        assert loaded_state["completed_steps"] == ["step1"]
    
    @pytest.mark.asyncio
    async def test_create_checkpoint(self, state_manager):
        """Test creating workflow checkpoints"""
        workflow_id = "test-workflow-456"
        
        # Create initial state
        await state_manager.save_workflow_state(workflow_id, {"status": "running"})
        
        # Create checkpoint
        checkpoint_data = {"step": "analysis_complete", "data": {"results": "test"}}
        success = await state_manager.create_checkpoint(
            workflow_id, "analysis_checkpoint", checkpoint_data
        )
        assert success is True
        
        # List checkpoints
        checkpoints = await state_manager.list_checkpoints(workflow_id)
        assert len(checkpoints) == 1
        assert checkpoints[0]["name"] == "analysis_checkpoint"
    
    @pytest.mark.asyncio
    async def test_restore_checkpoint(self, state_manager):
        """Test restoring from checkpoint"""
        workflow_id = "test-workflow-789"
        
        # Create state and checkpoint
        await state_manager.save_workflow_state(workflow_id, {"status": "running"})
        checkpoint_data = {"restored": True}
        await state_manager.create_checkpoint(workflow_id, "test_checkpoint", checkpoint_data)
        
        # Restore from checkpoint
        restored_data = await state_manager.restore_from_checkpoint(
            workflow_id, "test_checkpoint"
        )
        assert restored_data is not None
        assert restored_data["restored"] is True


class TestWorkflowNodes:
    """Test workflow nodes"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="AI response")
        return client
    
    @pytest.fixture
    def nodes(self, mock_llm_client):
        """Workflow nodes instance"""
        return WorkflowNodes(mock_llm_client)
    
    @pytest.mark.asyncio
    async def test_log_message_node(self, nodes):
        """Test log message node"""
        inputs = {"message": "Test log message", "level": "info"}
        result = await nodes.execute_node("log_message", inputs)
        
        assert result is not None
        assert result["message"] == "Test log message"
        assert result["level"] == "info"
    
    @pytest.mark.asyncio
    async def test_sleep_node(self, nodes):
        """Test sleep node"""
        inputs = {"duration": 0.1}  # Short duration for testing
        result = await nodes.execute_node("sleep", inputs)
        
        assert result is not None
        assert result["slept_duration"] == 0.1
    
    @pytest.mark.asyncio
    async def test_conditional_node(self, nodes):
        """Test conditional node"""
        # Test true condition
        inputs = {"condition": True, "true_value": "yes", "false_value": "no"}
        result = await nodes.execute_node("conditional", inputs)
        
        assert result is not None
        assert result["result"] == "yes"
        assert result["branch_taken"] == "true"
        
        # Test false condition
        inputs = {"condition": False, "true_value": "yes", "false_value": "no"}
        result = await nodes.execute_node("conditional", inputs)
        
        assert result["result"] == "no"
        assert result["branch_taken"] == "false"
    
    @pytest.mark.asyncio
    async def test_ai_chat_node(self, nodes):
        """Test AI chat node"""
        inputs = {"prompt": "Test prompt", "system_message": "You are helpful"}
        result = await nodes.execute_node("ai_chat", inputs)
        
        assert result is not None
        assert result["ai_response"] == "AI response"
        assert result["prompt"] == "Test prompt"
    
    def test_get_available_nodes(self, nodes):
        """Test getting available node types"""
        available = nodes.get_available_nodes()
        assert len(available) > 0
        assert "log_message" in available
        assert "ai_chat" in available
        assert "conditional" in available


class TestWorkflowCommands:
    """Test workflow CLI commands"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="Command response")
        return client
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def commands(self, mock_llm_client, temp_workspace):
        """Workflow commands instance"""
        return WorkflowCommands(mock_llm_client, temp_workspace)
    
    @pytest.mark.asyncio
    async def test_list_templates_command(self, commands):
        """Test list templates command"""
        result = await commands.list_templates()
        assert "workflow templates" in result.lower()
    
    @pytest.mark.asyncio
    async def test_create_workflow_from_template(self, commands):
        """Test creating workflow from template"""
        custom_inputs = {"project_name": "test_project"}
        result = await commands.create_workflow_from_template(
            "project_initialization", custom_inputs
        )
        assert "workflow created" in result.lower()
    
    @pytest.mark.asyncio
    async def test_workflow_statistics(self, commands):
        """Test getting workflow statistics"""
        result = await commands.get_workflow_statistics()
        assert "statistics retrieved" in result.lower()


class TestIntegration:
    """Integration tests for the complete workflow system"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for integration tests"""
        client = Mock()
        client.achat_completion = AsyncMock(return_value="Integration test response")
        return client
    
    @pytest.fixture
    def temp_workspace(self):
        """Temporary workspace for integration tests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('Hello, World!')")
            yield temp_dir
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, mock_llm_client, temp_workspace):
        """Test complete workflow execution end-to-end"""
        # Create workflow engine
        engine = WorkflowEngine(mock_llm_client, temp_workspace)
        
        # Create a simple workflow
        steps = [
            {
                "id": "scan",
                "name": "Scan Project",
                "description": "Scan project files",
                "node_type": "scan_project",
                "inputs": {"project_path": temp_workspace}
            },
            {
                "id": "log",
                "name": "Log Results",
                "description": "Log scan results",
                "node_type": "log_message",
                "inputs": {"message": "Scan completed"}
            }
        ]
        
        dependencies = {"log": ["scan"]}
        
        # Create workflow
        workflow_id = await engine.create_workflow(
            name="Integration Test",
            description="End-to-end integration test",
            steps=steps,
            dependencies=dependencies
        )
        
        # Execute workflow
        success = await engine.execute_workflow(workflow_id)
        assert success is True
        
        # Check final status
        status = engine.get_workflow_status(workflow_id)
        assert status["completed_steps"] == 2
        assert status["failed_steps"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
