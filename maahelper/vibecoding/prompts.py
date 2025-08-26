#!/usr/bin/env python3
"""
Vibecoding System Prompts
Specialized prompts for different coding scenarios and contexts
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Template for vibecoding prompts"""
    name: str
    description: str
    template: str
    variables: List[str]
    category: str


class VibecodingPrompts:
    """Collection of specialized prompts for vibecoding"""
    
    def __init__(self):
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, PromptTemplate]:
        """Initialize all vibecoding prompts"""
        return {
            # Code Analysis Prompts
            "code_review": PromptTemplate(
                name="code_review",
                description="Comprehensive code review with suggestions",
                template="""
You are an expert code reviewer. Analyze the following code and provide:

1. **Code Quality Assessment**
   - Overall structure and organization
   - Readability and maintainability
   - Performance considerations

2. **Issues Found**
   - Bugs or potential errors
   - Security vulnerabilities
   - Code smells and anti-patterns

3. **Improvement Suggestions**
   - Specific refactoring recommendations
   - Best practices to implement
   - Performance optimizations

4. **Positive Aspects**
   - Well-implemented features
   - Good practices observed

**Code to Review:**
```{language}
{code}
```

**Context:** {context}
**Focus Areas:** {focus_areas}

Please provide actionable feedback with specific examples and code snippets where helpful.
""",
                variables=["language", "code", "context", "focus_areas"],
                category="analysis"
            ),
            
            "bug_analysis": PromptTemplate(
                name="bug_analysis",
                description="Deep analysis of bugs and error conditions",
                template="""
You are a debugging expert. Analyze the following issue:

**Problem Description:** {problem}

**Code Context:**
```{language}
{code}
```

**Error/Symptoms:** {error_details}

**Environment:** {environment}

Please provide:

1. **Root Cause Analysis**
   - Identify the underlying cause
   - Explain why this issue occurs

2. **Step-by-Step Solution**
   - Specific fixes to implement
   - Code changes needed

3. **Prevention Strategies**
   - How to avoid similar issues
   - Testing recommendations

4. **Alternative Approaches**
   - Different ways to solve the problem
   - Trade-offs of each approach

Provide working code examples for your solutions.
""",
                variables=["problem", "language", "code", "error_details", "environment"],
                category="debugging"
            ),
            
            "architecture_design": PromptTemplate(
                name="architecture_design",
                description="System architecture and design guidance",
                template="""
You are a software architect. Help design a solution for:

**Requirements:** {requirements}

**Constraints:** {constraints}

**Current System:** {current_system}

**Scale/Performance Needs:** {scale_requirements}

Please provide:

1. **Architecture Overview**
   - High-level system design
   - Component relationships
   - Data flow diagrams (in text)

2. **Technology Stack Recommendations**
   - Languages and frameworks
   - Databases and storage
   - Infrastructure considerations

3. **Design Patterns**
   - Applicable design patterns
   - Implementation strategies

4. **Scalability Plan**
   - How to handle growth
   - Performance optimization points

5. **Implementation Roadmap**
   - Phase-by-phase development plan
   - Priority order of components

Include code examples and architectural diagrams in text format.
""",
                variables=["requirements", "constraints", "current_system", "scale_requirements"],
                category="architecture"
            ),
            
            # Code Generation Prompts
            "feature_implementation": PromptTemplate(
                name="feature_implementation",
                description="Complete feature implementation with tests",
                template="""
You are a senior developer. Implement the following feature:

**Feature Description:** {feature_description}

**Requirements:**
{requirements}

**Existing Codebase Context:**
```{language}
{existing_code}
```

**Technology Stack:** {tech_stack}

**Constraints:** {constraints}

Please provide:

1. **Complete Implementation**
   - All necessary code files
   - Proper error handling
   - Documentation/comments

2. **Unit Tests**
   - Comprehensive test coverage
   - Edge case testing
   - Mock implementations where needed

3. **Integration Instructions**
   - How to integrate with existing code
   - Configuration changes needed
   - Database migrations if applicable

4. **Usage Examples**
   - How to use the new feature
   - API documentation
   - Example calls/usage

Ensure code follows best practices and is production-ready.
""",
                variables=["feature_description", "requirements", "language", "existing_code", "tech_stack", "constraints"],
                category="implementation"
            ),
            
            "refactoring": PromptTemplate(
                name="refactoring",
                description="Code refactoring with improvement focus",
                template="""
You are a refactoring expert. Improve the following code:

**Current Code:**
```{language}
{code}
```

**Refactoring Goals:** {goals}

**Constraints:** {constraints}

**Performance Requirements:** {performance_requirements}

Please provide:

1. **Refactored Code**
   - Improved structure and readability
   - Better performance where possible
   - Enhanced maintainability

2. **Changes Explanation**
   - What was changed and why
   - Benefits of each change
   - Potential risks or considerations

3. **Migration Strategy**
   - How to safely apply changes
   - Backward compatibility considerations
   - Testing strategy

4. **Before/After Comparison**
   - Key improvements achieved
   - Metrics that should improve
   - Validation methods

Ensure the refactored code maintains the same functionality while improving quality.
""",
                variables=["language", "code", "goals", "constraints", "performance_requirements"],
                category="refactoring"
            ),
            
            # Learning and Explanation Prompts
            "concept_explanation": PromptTemplate(
                name="concept_explanation",
                description="Detailed explanation of programming concepts",
                template="""
You are a programming instructor. Explain the following concept:

**Concept:** {concept}

**Context/Use Case:** {context}

**Audience Level:** {audience_level}

**Specific Questions:** {questions}

Please provide:

1. **Clear Explanation**
   - Simple, understandable definition
   - Why this concept is important
   - When and where to use it

2. **Practical Examples**
   - Real-world code examples
   - Step-by-step implementation
   - Common use cases

3. **Best Practices**
   - How to implement correctly
   - Common mistakes to avoid
   - Performance considerations

4. **Related Concepts**
   - Connected topics to explore
   - Prerequisites to understand
   - Advanced applications

5. **Hands-on Exercise**
   - Practice problem to solve
   - Expected solution approach
   - Learning objectives

Make the explanation engaging and practical with plenty of examples.
""",
                variables=["concept", "context", "audience_level", "questions"],
                category="learning"
            ),
            
            # Optimization Prompts
            "performance_optimization": PromptTemplate(
                name="performance_optimization",
                description="Performance analysis and optimization",
                template="""
You are a performance optimization expert. Analyze and optimize:

**Current Code:**
```{language}
{code}
```

**Performance Issues:** {performance_issues}

**Constraints:** {constraints}

**Target Metrics:** {target_metrics}

**Environment:** {environment}

Please provide:

1. **Performance Analysis**
   - Bottlenecks identified
   - Resource usage patterns
   - Complexity analysis

2. **Optimization Strategy**
   - Specific optimizations to apply
   - Expected performance gains
   - Implementation priority

3. **Optimized Code**
   - Improved implementation
   - Benchmarking code
   - Performance measurements

4. **Trade-offs Discussion**
   - Memory vs speed considerations
   - Complexity vs performance
   - Maintainability impact

5. **Monitoring Recommendations**
   - Key metrics to track
   - Performance testing strategy
   - Regression prevention

Include before/after performance comparisons where possible.
""",
                variables=["language", "code", "performance_issues", "constraints", "target_metrics", "environment"],
                category="optimization"
            )
        }
    
    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        return self.prompts.get(name)
    
    def list_prompts(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List all prompts, optionally filtered by category"""
        if category:
            return [prompt for prompt in self.prompts.values() if prompt.category == category]
        return list(self.prompts.values())
    
    def get_categories(self) -> List[str]:
        """Get all available prompt categories"""
        return list(set(prompt.category for prompt in self.prompts.values()))
    
    def format_prompt(self, name: str, **kwargs) -> Optional[str]:
        """Format a prompt template with provided variables"""
        prompt = self.get_prompt(name)
        if not prompt:
            return None
        
        try:
            return prompt.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable for prompt '{name}': {e}")
    
    def validate_variables(self, name: str, variables: Dict[str, Any]) -> List[str]:
        """Validate that all required variables are provided"""
        prompt = self.get_prompt(name)
        if not prompt:
            return [f"Prompt '{name}' not found"]
        
        missing = []
        for var in prompt.variables:
            if var not in variables:
                missing.append(var)
        
        return missing


# Global instance
vibecoding_prompts = VibecodingPrompts()
