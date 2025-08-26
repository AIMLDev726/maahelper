"""
Workflow Templates for MaaHelper
Predefined workflow templates for common coding tasks
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class WorkflowTemplate:
    """Template for creating workflows"""
    name: str
    description: str
    category: str
    steps: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    default_inputs: Dict[str, Any]
    tags: List[str]

class WorkflowTemplates:
    """
    Collection of predefined workflow templates for common coding tasks
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, WorkflowTemplate]:
        """Initialize all workflow templates"""
        templates = {}
        
        # Code Quality Workflows
        templates['code_quality_audit'] = self._create_code_quality_audit_template()
        templates['comprehensive_refactor'] = self._create_comprehensive_refactor_template()
        templates['security_audit'] = self._create_security_audit_template()
        
        # Testing Workflows
        templates['test_suite_generation'] = self._create_test_suite_generation_template()
        templates['test_coverage_improvement'] = self._create_test_coverage_improvement_template()
        
        # Documentation Workflows
        templates['documentation_generation'] = self._create_documentation_generation_template()
        templates['api_documentation'] = self._create_api_documentation_template()
        
        # Feature Development Workflows
        templates['feature_implementation'] = self._create_feature_implementation_template()
        templates['bug_fix_workflow'] = self._create_bug_fix_workflow_template()
        templates['performance_optimization'] = self._create_performance_optimization_template()
        
        # Project Setup Workflows
        templates['project_initialization'] = self._create_project_initialization_template()
        templates['ci_cd_setup'] = self._create_ci_cd_setup_template()
        
        # Maintenance Workflows
        templates['dependency_update'] = self._create_dependency_update_template()
        templates['code_cleanup'] = self._create_code_cleanup_template()
        
        return templates
    
    def get_template(self, template_name: str) -> WorkflowTemplate:
        """Get a specific workflow template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        return self.templates[template_name]
    
    def list_templates(self, category: str = None) -> List[WorkflowTemplate]:
        """List available templates, optionally filtered by category"""
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates
    
    def get_categories(self) -> List[str]:
        """Get all available template categories"""
        return list(set(t.category for t in self.templates.values()))
    
    # Template Definitions
    def _create_code_quality_audit_template(self) -> WorkflowTemplate:
        """Comprehensive code quality audit workflow"""
        return WorkflowTemplate(
            name="Code Quality Audit",
            description="Comprehensive analysis of code quality across the entire project",
            category="code_quality",
            steps=[
                {
                    "id": "scan_project",
                    "name": "Scan Project Structure",
                    "description": "Analyze project structure and identify all code files",
                    "node_type": "scan_project",
                    "inputs": {"include_hidden": False}
                },
                {
                    "id": "analyze_files",
                    "name": "Analyze Code Files",
                    "description": "Perform detailed analysis of each code file",
                    "node_type": "parallel",
                    "inputs": {
                        "operations": [
                            {"node_type": "code_review", "inputs": {}},
                            {"node_type": "bug_analysis", "inputs": {}},
                            {"node_type": "performance_analysis", "inputs": {}}
                        ]
                    }
                },
                {
                    "id": "generate_report",
                    "name": "Generate Quality Report",
                    "description": "Compile comprehensive quality report",
                    "node_type": "ai_generate",
                    "inputs": {
                        "content_type": "quality_report",
                        "prompt": "Generate comprehensive code quality report"
                    }
                },
                {
                    "id": "save_report",
                    "name": "Save Quality Report",
                    "description": "Save the quality report to file",
                    "node_type": "write_file",
                    "inputs": {
                        "file_path": "quality_report.md",
                        "create_dirs": True
                    }
                }
            ],
            dependencies={
                "analyze_files": ["scan_project"],
                "generate_report": ["analyze_files"],
                "save_report": ["generate_report"]
            },
            default_inputs={
                "project_path": ".",
                "output_format": "markdown"
            },
            tags=["quality", "analysis", "audit"]
        )
    
    def _create_comprehensive_refactor_template(self) -> WorkflowTemplate:
        """Comprehensive code refactoring workflow"""
        return WorkflowTemplate(
            name="Comprehensive Refactor",
            description="Systematic refactoring of code for improved quality and maintainability",
            category="refactoring",
            steps=[
                {
                    "id": "backup_code",
                    "name": "Create Backup",
                    "description": "Create git branch for refactoring work",
                    "node_type": "git_branch",
                    "inputs": {"branch_name": "refactor-workflow"}
                },
                {
                    "id": "analyze_code",
                    "name": "Analyze Current Code",
                    "description": "Analyze code to identify refactoring opportunities",
                    "node_type": "code_review",
                    "inputs": {"focus_areas": "refactoring opportunities"}
                },
                {
                    "id": "refactor_code",
                    "name": "Refactor Code",
                    "description": "Apply refactoring improvements",
                    "node_type": "refactor_code",
                    "inputs": {"refactor_goals": "improve maintainability and readability"}
                },
                {
                    "id": "generate_tests",
                    "name": "Generate Tests",
                    "description": "Generate tests for refactored code",
                    "node_type": "generate_tests",
                    "inputs": {}
                },
                {
                    "id": "run_tests",
                    "name": "Run Tests",
                    "description": "Verify refactored code works correctly",
                    "node_type": "run_tests",
                    "inputs": {}
                },
                {
                    "id": "commit_changes",
                    "name": "Commit Changes",
                    "description": "Commit refactored code",
                    "node_type": "git_commit",
                    "inputs": {"message": "Refactor: Improve code quality and maintainability"}
                }
            ],
            dependencies={
                "analyze_code": ["backup_code"],
                "refactor_code": ["analyze_code"],
                "generate_tests": ["refactor_code"],
                "run_tests": ["generate_tests"],
                "commit_changes": ["run_tests"]
            },
            default_inputs={
                "target_files": [],
                "refactor_scope": "full"
            },
            tags=["refactoring", "quality", "maintenance"]
        )
    
    def _create_test_suite_generation_template(self) -> WorkflowTemplate:
        """Test suite generation workflow"""
        return WorkflowTemplate(
            name="Test Suite Generation",
            description="Generate comprehensive test suite for the project",
            category="testing",
            steps=[
                {
                    "id": "scan_source_files",
                    "name": "Scan Source Files",
                    "description": "Identify all source files that need tests",
                    "node_type": "scan_project",
                    "inputs": {"file_patterns": ["*.py", "*.js", "*.ts"]}
                },
                {
                    "id": "analyze_functions",
                    "name": "Analyze Functions",
                    "description": "Analyze functions and classes to understand test requirements",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "test_requirements"}
                },
                {
                    "id": "generate_unit_tests",
                    "name": "Generate Unit Tests",
                    "description": "Generate unit tests for each module",
                    "node_type": "generate_tests",
                    "inputs": {"test_type": "unit"}
                },
                {
                    "id": "generate_integration_tests",
                    "name": "Generate Integration Tests",
                    "description": "Generate integration tests",
                    "node_type": "generate_tests",
                    "inputs": {"test_type": "integration"}
                },
                {
                    "id": "create_test_structure",
                    "name": "Create Test Directory Structure",
                    "description": "Create proper test directory structure",
                    "node_type": "create_directory",
                    "inputs": {"dir_path": "tests"}
                },
                {
                    "id": "save_tests",
                    "name": "Save Test Files",
                    "description": "Save generated tests to appropriate files",
                    "node_type": "write_file",
                    "inputs": {"create_dirs": True}
                }
            ],
            dependencies={
                "analyze_functions": ["scan_source_files"],
                "generate_unit_tests": ["analyze_functions"],
                "generate_integration_tests": ["analyze_functions"],
                "create_test_structure": ["analyze_functions"],
                "save_tests": ["generate_unit_tests", "generate_integration_tests", "create_test_structure"]
            },
            default_inputs={
                "test_framework": "pytest",
                "coverage_target": 80
            },
            tags=["testing", "quality", "automation"]
        )
    
    def _create_documentation_generation_template(self) -> WorkflowTemplate:
        """Documentation generation workflow"""
        return WorkflowTemplate(
            name="Documentation Generation",
            description="Generate comprehensive documentation for the project",
            category="documentation",
            steps=[
                {
                    "id": "scan_code_files",
                    "name": "Scan Code Files",
                    "description": "Identify all files that need documentation",
                    "node_type": "scan_project",
                    "inputs": {}
                },
                {
                    "id": "generate_api_docs",
                    "name": "Generate API Documentation",
                    "description": "Generate API documentation from code",
                    "node_type": "generate_docs",
                    "inputs": {"doc_type": "api"}
                },
                {
                    "id": "generate_user_guide",
                    "name": "Generate User Guide",
                    "description": "Generate user guide and tutorials",
                    "node_type": "ai_generate",
                    "inputs": {
                        "content_type": "user_guide",
                        "prompt": "Generate comprehensive user guide"
                    }
                },
                {
                    "id": "generate_readme",
                    "name": "Generate README",
                    "description": "Generate or update README file",
                    "node_type": "ai_generate",
                    "inputs": {
                        "content_type": "readme",
                        "prompt": "Generate comprehensive README"
                    }
                },
                {
                    "id": "create_docs_structure",
                    "name": "Create Documentation Structure",
                    "description": "Create documentation directory structure",
                    "node_type": "create_directory",
                    "inputs": {"dir_path": "docs"}
                },
                {
                    "id": "save_documentation",
                    "name": "Save Documentation",
                    "description": "Save all generated documentation",
                    "node_type": "parallel",
                    "inputs": {
                        "operations": [
                            {"node_type": "write_file", "inputs": {"file_path": "docs/api.md"}},
                            {"node_type": "write_file", "inputs": {"file_path": "docs/user_guide.md"}},
                            {"node_type": "write_file", "inputs": {"file_path": "README.md"}}
                        ]
                    }
                }
            ],
            dependencies={
                "generate_api_docs": ["scan_code_files"],
                "generate_user_guide": ["scan_code_files"],
                "generate_readme": ["scan_code_files"],
                "create_docs_structure": ["scan_code_files"],
                "save_documentation": ["generate_api_docs", "generate_user_guide", "generate_readme", "create_docs_structure"]
            },
            default_inputs={
                "doc_format": "markdown",
                "include_examples": True
            },
            tags=["documentation", "api", "user_guide"]
        )
    
    def _create_feature_implementation_template(self) -> WorkflowTemplate:
        """Feature implementation workflow"""
        return WorkflowTemplate(
            name="Feature Implementation",
            description="Complete workflow for implementing a new feature",
            category="development",
            steps=[
                {
                    "id": "create_feature_branch",
                    "name": "Create Feature Branch",
                    "description": "Create a new branch for feature development",
                    "node_type": "git_branch",
                    "inputs": {}
                },
                {
                    "id": "analyze_requirements",
                    "name": "Analyze Requirements",
                    "description": "Analyze and understand feature requirements",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "requirements"}
                },
                {
                    "id": "design_architecture",
                    "name": "Design Architecture",
                    "description": "Design the feature architecture",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "architecture_design"}
                },
                {
                    "id": "implement_feature",
                    "name": "Implement Feature",
                    "description": "Generate feature implementation code",
                    "node_type": "generate_code",
                    "inputs": {}
                },
                {
                    "id": "generate_tests",
                    "name": "Generate Tests",
                    "description": "Generate tests for the new feature",
                    "node_type": "generate_tests",
                    "inputs": {}
                },
                {
                    "id": "run_tests",
                    "name": "Run Tests",
                    "description": "Run tests to verify feature works",
                    "node_type": "run_tests",
                    "inputs": {}
                },
                {
                    "id": "generate_docs",
                    "name": "Generate Documentation",
                    "description": "Generate documentation for the feature",
                    "node_type": "generate_docs",
                    "inputs": {}
                },
                {
                    "id": "commit_feature",
                    "name": "Commit Feature",
                    "description": "Commit the completed feature",
                    "node_type": "git_commit",
                    "inputs": {}
                }
            ],
            dependencies={
                "analyze_requirements": ["create_feature_branch"],
                "design_architecture": ["analyze_requirements"],
                "implement_feature": ["design_architecture"],
                "generate_tests": ["implement_feature"],
                "run_tests": ["generate_tests"],
                "generate_docs": ["implement_feature"],
                "commit_feature": ["run_tests", "generate_docs"]
            },
            default_inputs={
                "feature_name": "",
                "requirements": "",
                "target_language": "python"
            },
            tags=["development", "feature", "implementation"]
        )
    
    def _create_bug_fix_workflow_template(self) -> WorkflowTemplate:
        """Bug fix workflow"""
        return WorkflowTemplate(
            name="Bug Fix Workflow",
            description="Systematic approach to identifying and fixing bugs",
            category="maintenance",
            steps=[
                {
                    "id": "create_bugfix_branch",
                    "name": "Create Bug Fix Branch",
                    "description": "Create branch for bug fix work",
                    "node_type": "git_branch",
                    "inputs": {}
                },
                {
                    "id": "analyze_bug",
                    "name": "Analyze Bug",
                    "description": "Analyze the bug and understand root cause",
                    "node_type": "bug_analysis",
                    "inputs": {}
                },
                {
                    "id": "identify_affected_code",
                    "name": "Identify Affected Code",
                    "description": "Identify all code areas affected by the bug",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "impact_analysis"}
                },
                {
                    "id": "implement_fix",
                    "name": "Implement Fix",
                    "description": "Implement the bug fix",
                    "node_type": "refactor_code",
                    "inputs": {"refactor_goals": "fix identified bug"}
                },
                {
                    "id": "generate_regression_tests",
                    "name": "Generate Regression Tests",
                    "description": "Generate tests to prevent regression",
                    "node_type": "generate_tests",
                    "inputs": {"test_type": "regression"}
                },
                {
                    "id": "run_all_tests",
                    "name": "Run All Tests",
                    "description": "Run complete test suite to verify fix",
                    "node_type": "run_tests",
                    "inputs": {"test_scope": "all"}
                },
                {
                    "id": "commit_fix",
                    "name": "Commit Fix",
                    "description": "Commit the bug fix",
                    "node_type": "git_commit",
                    "inputs": {}
                }
            ],
            dependencies={
                "analyze_bug": ["create_bugfix_branch"],
                "identify_affected_code": ["analyze_bug"],
                "implement_fix": ["identify_affected_code"],
                "generate_regression_tests": ["implement_fix"],
                "run_all_tests": ["generate_regression_tests"],
                "commit_fix": ["run_all_tests"]
            },
            default_inputs={
                "bug_description": "",
                "error_logs": "",
                "reproduction_steps": ""
            },
            tags=["bugfix", "maintenance", "testing"]
        )
    
    def _create_performance_optimization_template(self) -> WorkflowTemplate:
        """Performance optimization workflow"""
        return WorkflowTemplate(
            name="Performance Optimization",
            description="Systematic performance analysis and optimization",
            category="optimization",
            steps=[
                {
                    "id": "baseline_performance",
                    "name": "Measure Baseline Performance",
                    "description": "Measure current performance metrics",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "performance_baseline"}
                },
                {
                    "id": "identify_bottlenecks",
                    "name": "Identify Bottlenecks",
                    "description": "Identify performance bottlenecks",
                    "node_type": "performance_analysis",
                    "inputs": {}
                },
                {
                    "id": "optimize_code",
                    "name": "Optimize Code",
                    "description": "Apply performance optimizations",
                    "node_type": "refactor_code",
                    "inputs": {"refactor_goals": "performance optimization"}
                },
                {
                    "id": "generate_performance_tests",
                    "name": "Generate Performance Tests",
                    "description": "Generate performance tests",
                    "node_type": "generate_tests",
                    "inputs": {"test_type": "performance"}
                },
                {
                    "id": "measure_improvements",
                    "name": "Measure Improvements",
                    "description": "Measure performance improvements",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "performance_comparison"}
                },
                {
                    "id": "generate_report",
                    "name": "Generate Performance Report",
                    "description": "Generate performance optimization report",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "performance_report"}
                }
            ],
            dependencies={
                "identify_bottlenecks": ["baseline_performance"],
                "optimize_code": ["identify_bottlenecks"],
                "generate_performance_tests": ["optimize_code"],
                "measure_improvements": ["generate_performance_tests"],
                "generate_report": ["measure_improvements"]
            },
            default_inputs={
                "performance_targets": {},
                "optimization_focus": "general"
            },
            tags=["performance", "optimization", "analysis"]
        )
    
    def _create_security_audit_template(self) -> WorkflowTemplate:
        """Security audit workflow"""
        return WorkflowTemplate(
            name="Security Audit",
            description="Comprehensive security analysis of the codebase",
            category="security",
            steps=[
                {
                    "id": "scan_dependencies",
                    "name": "Scan Dependencies",
                    "description": "Scan for vulnerable dependencies",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "dependency_security"}
                },
                {
                    "id": "analyze_code_security",
                    "name": "Analyze Code Security",
                    "description": "Analyze code for security vulnerabilities",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "security_vulnerabilities"}
                },
                {
                    "id": "check_configurations",
                    "name": "Check Security Configurations",
                    "description": "Review security configurations",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "security_config"}
                },
                {
                    "id": "generate_security_report",
                    "name": "Generate Security Report",
                    "description": "Compile comprehensive security report",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "security_report"}
                },
                {
                    "id": "recommend_fixes",
                    "name": "Recommend Security Fixes",
                    "description": "Generate recommendations for security improvements",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "security_recommendations"}
                }
            ],
            dependencies={
                "analyze_code_security": ["scan_dependencies"],
                "check_configurations": ["scan_dependencies"],
                "generate_security_report": ["analyze_code_security", "check_configurations"],
                "recommend_fixes": ["generate_security_report"]
            },
            default_inputs={
                "security_standards": ["OWASP"],
                "compliance_requirements": []
            },
            tags=["security", "audit", "compliance"]
        )
    
    def _create_project_initialization_template(self) -> WorkflowTemplate:
        """Project initialization workflow"""
        return WorkflowTemplate(
            name="Project Initialization",
            description="Set up a new project with best practices",
            category="setup",
            steps=[
                {
                    "id": "create_structure",
                    "name": "Create Project Structure",
                    "description": "Create standard project directory structure",
                    "node_type": "parallel",
                    "inputs": {
                        "operations": [
                            {"node_type": "create_directory", "inputs": {"dir_path": "src"}},
                            {"node_type": "create_directory", "inputs": {"dir_path": "tests"}},
                            {"node_type": "create_directory", "inputs": {"dir_path": "docs"}},
                            {"node_type": "create_directory", "inputs": {"dir_path": "scripts"}}
                        ]
                    }
                },
                {
                    "id": "generate_readme",
                    "name": "Generate README",
                    "description": "Generate initial README file",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "project_readme"}
                },
                {
                    "id": "create_gitignore",
                    "name": "Create .gitignore",
                    "description": "Generate appropriate .gitignore file",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "gitignore"}
                },
                {
                    "id": "setup_testing",
                    "name": "Setup Testing Framework",
                    "description": "Setup testing framework and configuration",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "test_config"}
                },
                {
                    "id": "create_license",
                    "name": "Create License",
                    "description": "Generate license file",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "license"}
                },
                {
                    "id": "init_git",
                    "name": "Initialize Git",
                    "description": "Initialize git repository",
                    "node_type": "git_commit",
                    "inputs": {"message": "Initial commit"}
                }
            ],
            dependencies={
                "generate_readme": ["create_structure"],
                "create_gitignore": ["create_structure"],
                "setup_testing": ["create_structure"],
                "create_license": ["create_structure"],
                "init_git": ["generate_readme", "create_gitignore", "setup_testing", "create_license"]
            },
            default_inputs={
                "project_name": "",
                "project_type": "python",
                "license_type": "MIT"
            },
            tags=["setup", "initialization", "project"]
        )
    
    def _create_ci_cd_setup_template(self) -> WorkflowTemplate:
        """CI/CD setup workflow"""
        return WorkflowTemplate(
            name="CI/CD Setup",
            description="Set up continuous integration and deployment",
            category="devops",
            steps=[
                {
                    "id": "analyze_project",
                    "name": "Analyze Project",
                    "description": "Analyze project to determine CI/CD requirements",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "cicd_requirements"}
                },
                {
                    "id": "generate_github_actions",
                    "name": "Generate GitHub Actions",
                    "description": "Generate GitHub Actions workflow files",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "github_actions"}
                },
                {
                    "id": "create_docker_config",
                    "name": "Create Docker Configuration",
                    "description": "Generate Dockerfile and docker-compose",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "docker_config"}
                },
                {
                    "id": "setup_testing_pipeline",
                    "name": "Setup Testing Pipeline",
                    "description": "Configure automated testing pipeline",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "test_pipeline"}
                },
                {
                    "id": "create_deployment_config",
                    "name": "Create Deployment Configuration",
                    "description": "Generate deployment configuration",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "deployment_config"}
                }
            ],
            dependencies={
                "generate_github_actions": ["analyze_project"],
                "create_docker_config": ["analyze_project"],
                "setup_testing_pipeline": ["analyze_project"],
                "create_deployment_config": ["analyze_project"]
            },
            default_inputs={
                "ci_platform": "github_actions",
                "deployment_target": "cloud",
                "testing_framework": "pytest"
            },
            tags=["cicd", "devops", "automation"]
        )
    
    def _create_dependency_update_template(self) -> WorkflowTemplate:
        """Dependency update workflow"""
        return WorkflowTemplate(
            name="Dependency Update",
            description="Safely update project dependencies",
            category="maintenance",
            steps=[
                {
                    "id": "analyze_dependencies",
                    "name": "Analyze Current Dependencies",
                    "description": "Analyze current dependency versions",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "dependency_analysis"}
                },
                {
                    "id": "check_vulnerabilities",
                    "name": "Check for Vulnerabilities",
                    "description": "Check dependencies for security vulnerabilities",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "vulnerability_scan"}
                },
                {
                    "id": "plan_updates",
                    "name": "Plan Updates",
                    "description": "Plan dependency update strategy",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "update_plan"}
                },
                {
                    "id": "run_tests_before",
                    "name": "Run Tests (Before)",
                    "description": "Run tests before updates",
                    "node_type": "run_tests",
                    "inputs": {}
                },
                {
                    "id": "update_dependencies",
                    "name": "Update Dependencies",
                    "description": "Apply dependency updates",
                    "node_type": "ai_generate",
                    "inputs": {"content_type": "dependency_updates"}
                },
                {
                    "id": "run_tests_after",
                    "name": "Run Tests (After)",
                    "description": "Run tests after updates",
                    "node_type": "run_tests",
                    "inputs": {}
                },
                {
                    "id": "commit_updates",
                    "name": "Commit Updates",
                    "description": "Commit dependency updates",
                    "node_type": "git_commit",
                    "inputs": {"message": "Update dependencies"}
                }
            ],
            dependencies={
                "check_vulnerabilities": ["analyze_dependencies"],
                "plan_updates": ["check_vulnerabilities"],
                "run_tests_before": ["plan_updates"],
                "update_dependencies": ["run_tests_before"],
                "run_tests_after": ["update_dependencies"],
                "commit_updates": ["run_tests_after"]
            },
            default_inputs={
                "update_strategy": "conservative",
                "include_dev_dependencies": True
            },
            tags=["maintenance", "dependencies", "security"]
        )
    
    def _create_code_cleanup_template(self) -> WorkflowTemplate:
        """Code cleanup workflow"""
        return WorkflowTemplate(
            name="Code Cleanup",
            description="Clean up and organize codebase",
            category="maintenance",
            steps=[
                {
                    "id": "scan_codebase",
                    "name": "Scan Codebase",
                    "description": "Scan entire codebase for cleanup opportunities",
                    "node_type": "scan_project",
                    "inputs": {}
                },
                {
                    "id": "identify_dead_code",
                    "name": "Identify Dead Code",
                    "description": "Identify unused code and imports",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "dead_code"}
                },
                {
                    "id": "check_code_style",
                    "name": "Check Code Style",
                    "description": "Check code style and formatting",
                    "node_type": "ai_analyze",
                    "inputs": {"analysis_type": "code_style"}
                },
                {
                    "id": "cleanup_imports",
                    "name": "Cleanup Imports",
                    "description": "Remove unused imports and organize",
                    "node_type": "refactor_code",
                    "inputs": {"refactor_goals": "cleanup imports"}
                },
                {
                    "id": "format_code",
                    "name": "Format Code",
                    "description": "Apply consistent code formatting",
                    "node_type": "refactor_code",
                    "inputs": {"refactor_goals": "format code"}
                },
                {
                    "id": "remove_dead_code",
                    "name": "Remove Dead Code",
                    "description": "Remove identified dead code",
                    "node_type": "refactor_code",
                    "inputs": {"refactor_goals": "remove dead code"}
                },
                {
                    "id": "run_tests",
                    "name": "Run Tests",
                    "description": "Verify cleanup didn't break anything",
                    "node_type": "run_tests",
                    "inputs": {}
                },
                {
                    "id": "commit_cleanup",
                    "name": "Commit Cleanup",
                    "description": "Commit code cleanup changes",
                    "node_type": "git_commit",
                    "inputs": {"message": "Code cleanup: remove dead code and improve formatting"}
                }
            ],
            dependencies={
                "identify_dead_code": ["scan_codebase"],
                "check_code_style": ["scan_codebase"],
                "cleanup_imports": ["check_code_style"],
                "format_code": ["cleanup_imports"],
                "remove_dead_code": ["identify_dead_code", "format_code"],
                "run_tests": ["remove_dead_code"],
                "commit_cleanup": ["run_tests"]
            },
            default_inputs={
                "preserve_comments": True,
                "aggressive_cleanup": False
            },
            tags=["cleanup", "maintenance", "formatting"]
        )
