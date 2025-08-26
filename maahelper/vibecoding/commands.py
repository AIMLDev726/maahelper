#!/usr/bin/env python3
"""
Vibecoding Commands
Command implementations for vibecoding workflow
"""

from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel

from .prompts import vibecoding_prompts

console = Console()


class VibecodingCommands:
    """Command implementations for vibecoding workflow"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.prompts = vibecoding_prompts
    
    async def code_review(self, code: str, language: str = "python", context: str = "", focus_areas: str = "") -> str:
        """Perform AI-powered code review"""
        try:
            prompt = self.prompts.format_prompt(
                "code_review",
                language=language,
                code=code,
                context=context,
                focus_areas=focus_areas
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for code review"
                
        except Exception as e:
            return f"❌ Error during code review: {e}"
    
    async def bug_analysis(self, problem: str, code: str, language: str = "python", 
                          error_details: str = "", environment: str = "") -> str:
        """Analyze bugs and provide solutions"""
        try:
            prompt = self.prompts.format_prompt(
                "bug_analysis",
                problem=problem,
                language=language,
                code=code,
                error_details=error_details,
                environment=environment
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for bug analysis"
                
        except Exception as e:
            return f"❌ Error during bug analysis: {e}"
    
    async def architecture_design(self, requirements: str, constraints: str = "", 
                                 current_system: str = "", scale_requirements: str = "") -> str:
        """Design system architecture"""
        try:
            prompt = self.prompts.format_prompt(
                "architecture_design",
                requirements=requirements,
                constraints=constraints,
                current_system=current_system,
                scale_requirements=scale_requirements
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for architecture design"
                
        except Exception as e:
            return f"❌ Error during architecture design: {e}"
    
    async def implement_feature(self, feature_description: str, requirements: str, 
                               language: str = "python", existing_code: str = "",
                               tech_stack: str = "", constraints: str = "") -> str:
        """Implement a complete feature"""
        try:
            prompt = self.prompts.format_prompt(
                "feature_implementation",
                feature_description=feature_description,
                requirements=requirements,
                language=language,
                existing_code=existing_code,
                tech_stack=tech_stack,
                constraints=constraints
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for feature implementation"
                
        except Exception as e:
            return f"❌ Error during feature implementation: {e}"
    
    async def refactor_code(self, code: str, language: str = "python", goals: str = "",
                           constraints: str = "", performance_requirements: str = "") -> str:
        """Refactor code for improvement"""
        try:
            prompt = self.prompts.format_prompt(
                "refactoring",
                language=language,
                code=code,
                goals=goals,
                constraints=constraints,
                performance_requirements=performance_requirements
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for refactoring"
                
        except Exception as e:
            return f"❌ Error during refactoring: {e}"
    
    async def explain_concept(self, concept: str, context: str = "", 
                             audience_level: str = "intermediate", questions: str = "") -> str:
        """Explain programming concepts"""
        try:
            prompt = self.prompts.format_prompt(
                "concept_explanation",
                concept=concept,
                context=context,
                audience_level=audience_level,
                questions=questions
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for concept explanation"
                
        except Exception as e:
            return f"❌ Error during concept explanation: {e}"
    
    async def optimize_performance(self, code: str, language: str = "python",
                                  performance_issues: str = "", constraints: str = "",
                                  target_metrics: str = "", environment: str = "") -> str:
        """Optimize code performance"""
        try:
            prompt = self.prompts.format_prompt(
                "performance_optimization",
                language=language,
                code=code,
                performance_issues=performance_issues,
                constraints=constraints,
                target_metrics=target_metrics,
                environment=environment
            )
            
            if self.llm_client:
                response = await self.llm_client.achat_completion([
                    {"role": "user", "content": prompt}
                ])
                return response
            else:
                return "❌ No LLM client available for performance optimization"
                
        except Exception as e:
            return f"❌ Error during performance optimization: {e}"
    
    def list_available_commands(self) -> str:
        """List all available vibecoding commands"""
        commands = [
            "🔍 **code-review** - Comprehensive code review with suggestions",
            "🐛 **bug-analysis** - Deep analysis of bugs and error conditions", 
            "🏗️ **architecture-design** - System architecture and design guidance",
            "⚡ **implement-feature** - Complete feature implementation with tests",
            "🔧 **refactor-code** - Code refactoring with improvement focus",
            "📚 **explain-concept** - Detailed explanation of programming concepts",
            "🚀 **optimize-performance** - Performance analysis and optimization"
        ]
        
        return "\n".join(commands)
    
    def get_command_help(self, command: str) -> str:
        """Get help for a specific command"""
        help_text = {
            "code-review": """
**Code Review Command**

Usage: Analyze code for quality, bugs, and improvements

Parameters:
- code: The code to review
- language: Programming language (default: python)
- context: Additional context about the code
- focus_areas: Specific areas to focus on

Example:
```
code-review --language python --context "API endpoint" --focus_areas "security,performance"
```
""",
            "bug-analysis": """
**Bug Analysis Command**

Usage: Analyze and fix bugs in code

Parameters:
- problem: Description of the problem
- code: The problematic code
- language: Programming language (default: python)
- error_details: Error messages or symptoms
- environment: Runtime environment details

Example:
```
bug-analysis --problem "Function crashes" --error_details "IndexError: list index out of range"
```
""",
            "architecture-design": """
**Architecture Design Command**

Usage: Design system architecture and components

Parameters:
- requirements: System requirements
- constraints: Technical constraints
- current_system: Existing system description
- scale_requirements: Scalability needs

Example:
```
architecture-design --requirements "User authentication system" --scale_requirements "10k users"
```
"""
        }
        
        return help_text.get(command, f"No help available for command: {command}")


# Global instance
vibecoding_commands = VibecodingCommands()
