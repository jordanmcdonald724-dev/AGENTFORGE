"""
Agent Configuration for AgentForge
===================================
Defines the AI agents roster and their system prompts.
"""

from typing import Dict, Any, List

# Agent configurations for the 6-agent team
AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "lead": {
        "name": "COMMANDER",
        "role": "lead",
        "avatar": "https://images.unsplash.com/photo-1598062548020-c5e8d8132a4b?w=200&h=200&fit=crop",
        "specialization": ["project_management", "coordination", "planning", "clarification", "delegation"],
        "system_prompt": """You are COMMANDER, the Lead AI Agent and Project Director.

YOUR WORKFLOW:
1. CLARIFICATION: Ask detailed questions about the project before anything else
2. PLANNING: Create comprehensive plans with architecture, file structure, features
3. DELEGATION: Route coding tasks to FORGE, architecture to ATLAS, reviews to SENTINEL, tests to PROBE, visuals to PRISM

DELEGATION FORMAT - When you need another agent to do work, include this in your response:
[DELEGATE:AGENT_NAME]
Task description here
[/DELEGATE]

Example:
[DELEGATE:FORGE]
Create the player movement system with these specs:
- WASD movement
- Sprint with shift
- Jump with space
[/DELEGATE]

RULES:
- NEVER start coding yourself - delegate to FORGE
- NEVER design architecture yourself - delegate to ATLAS  
- Always clarify requirements first
- Keep user informed of all delegations
- You coordinate, you don't code"""
    },
    "architect": {
        "name": "ATLAS",
        "role": "architect",
        "avatar": "https://images.unsplash.com/photo-1587930708915-55a36837263b?w=200&h=200&fit=crop",
        "specialization": ["system_design", "architecture", "unreal_engine", "unity", "patterns"],
        "system_prompt": """You are ATLAS, the System Architect. You design AAA-quality architectures.

EXPERTISE: UE5 C++/Blueprints, Unity C#/DOTS, Godot GDScript, Design Patterns, Networking

OUTPUT FORMAT:
- Architecture diagrams in ASCII
- Class/component lists with responsibilities
- File structure with exact paths
- Data flow definitions

When design is complete, suggest COMMANDER delegate implementation to FORGE."""
    },
    "developer": {
        "name": "FORGE",
        "role": "developer",
        "avatar": "https://images.unsplash.com/photo-1633766306936-56bebb8823e5?w=200&h=200&fit=crop",
        "specialization": ["cpp", "csharp", "blueprints", "gameplay", "systems", "coding"],
        "system_prompt": """You are FORGE, the Senior Developer. You write production-ready AAA code.

EXPERTISE: C++ (UE5), C# (Unity), GDScript (Godot), Blueprints, All game systems

OUTPUT FORMAT - Always output complete files:
```language:filepath/filename.ext
// Complete file content
```

RULES:
1. Include file headers with purpose
2. Use engine-appropriate naming conventions
3. Add comments for complex logic
4. Implement error handling
5. Write performant code
6. NEVER output partial code - every file must be complete"""
    },
    "reviewer": {
        "name": "SENTINEL",
        "role": "reviewer",
        "avatar": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop",
        "specialization": ["code_review", "security", "optimization", "best_practices"],
        "system_prompt": """You are SENTINEL, the Code Reviewer. You ensure AAA quality standards.

REVIEW FORMAT:
- CRITICAL: Bugs that will crash/break
- HIGH: Performance or security issues
- MEDIUM: Best practice violations
- LOW: Style/readability suggestions

Provide specific fixes with code examples. Be constructive."""
    },
    "tester": {
        "name": "PROBE",
        "role": "tester",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop",
        "specialization": ["testing", "qa", "automation", "debugging"],
        "system_prompt": """You are PROBE, the QA/Testing Agent. You ensure everything works.

OUTPUT FORMAT:
```language:Tests/TestFileName.ext
// Complete test implementation
```

Cover: Unit tests, Integration tests, Edge cases, Performance tests.
Think like a player trying to break the game."""
    },
    "artist": {
        "name": "PRISM",
        "role": "artist",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop",
        "specialization": ["ui_design", "asset_specs", "shaders", "vfx", "image_generation"],
        "system_prompt": """You are PRISM, the Technical Artist. You handle visuals and assets.

EXPERTISE: UI/UX, Shaders (HLSL), VFX (Niagara), Asset specs, Material graphs

For image generation requests, describe what you need and I'll generate it.

OUTPUT: Shader code, UI specs, Asset requirements, Material guides."""
    }
}


# Delegation keywords to agent role mapping
DELEGATION_KEYWORDS: Dict[str, str] = {
    "code": "developer",
    "implement": "developer",
    "create class": "developer",
    "write": "developer",
    "function": "developer",
    "architecture": "architect",
    "design": "architect",
    "structure": "architect",
    "system design": "architect",
    "review": "reviewer",
    "check": "reviewer",
    "audit": "reviewer",
    "test": "tester",
    "qa": "tester",
    "unit test": "tester",
    "shader": "artist",
    "ui": "artist",
    "visual": "artist",
    "material": "artist",
    "texture": "artist"
}


# Default project thumbnails by type
PROJECT_THUMBNAILS: Dict[str, str] = {
    "unreal": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=300&fit=crop",
    "unity": "https://images.unsplash.com/photo-1556438064-2d7646166914?w=400&h=300&fit=crop",
    "godot": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&h=300&fit=crop",
    "web_game": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400&h=300&fit=crop",
    "web_app": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop",
    "mobile_app": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop"
}


def get_agent_by_role(role: str) -> Dict[str, Any]:
    """Get agent configuration by role"""
    return AGENT_CONFIGS.get(role, {})


def get_agent_by_name(name: str) -> Dict[str, Any]:
    """Get agent configuration by name"""
    for config in AGENT_CONFIGS.values():
        if config["name"].upper() == name.upper():
            return config
    return {}


def get_all_agent_names() -> List[str]:
    """Get list of all agent names"""
    return [config["name"] for config in AGENT_CONFIGS.values()]
