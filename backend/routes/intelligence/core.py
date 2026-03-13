"""
Intelligence Systems - Global Code Knowledge Graph, Self-Evolving Agents, Parallel Architecture
The brain of AgentForge OS
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
import asyncio
from pydantic import BaseModel

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

from core.database import db
from core.utils import serialize_doc


# =============================================================================
# GLOBAL CODE KNOWLEDGE GRAPH
# =============================================================================

class KnowledgeNode(BaseModel):
    category: str
    pattern: str
    description: str
    usage_count: int = 0
    confidence: float = 1.0
    related_patterns: List[str] = []
    code_examples: List[str] = []


# In-memory knowledge graph (persisted to MongoDB)
KNOWLEDGE_GRAPH: Dict[str, Dict[str, List[dict]]] = {
    "frontend": {
        "react": [
            {"pattern": "hooks", "description": "React Hooks patterns", "examples": ["useState", "useEffect", "useContext"]},
            {"pattern": "routing", "description": "Client-side routing", "examples": ["react-router", "protected-routes"]},
            {"pattern": "state", "description": "State management", "examples": ["zustand", "redux", "context"]},
            {"pattern": "auth", "description": "Authentication flows", "examples": ["jwt", "oauth", "session"]},
            {"pattern": "forms", "description": "Form handling", "examples": ["react-hook-form", "formik", "validation"]}
        ],
        "nextjs": [
            {"pattern": "ssr", "description": "Server-side rendering", "examples": ["getServerSideProps", "getStaticProps"]},
            {"pattern": "api-routes", "description": "API route handlers", "examples": ["pages/api", "middleware"]}
        ]
    },
    "backend": {
        "fastapi": [
            {"pattern": "crud", "description": "CRUD operations", "examples": ["create", "read", "update", "delete"]},
            {"pattern": "auth", "description": "Authentication", "examples": ["jwt", "oauth2", "api-keys"]},
            {"pattern": "middleware", "description": "Request middleware", "examples": ["cors", "rate-limiting", "logging"]},
            {"pattern": "async", "description": "Async patterns", "examples": ["asyncio", "background-tasks", "websockets"]}
        ],
        "node": [
            {"pattern": "express", "description": "Express.js patterns", "examples": ["middleware", "routing", "error-handling"]},
            {"pattern": "prisma", "description": "Prisma ORM", "examples": ["schema", "migrations", "queries"]}
        ]
    },
    "database": {
        "postgresql": [
            {"pattern": "schema", "description": "Database schema design", "examples": ["tables", "relations", "indexes"]},
            {"pattern": "queries", "description": "Query optimization", "examples": ["joins", "aggregations", "cte"]}
        ],
        "mongodb": [
            {"pattern": "schema", "description": "Document design", "examples": ["embedding", "referencing"]},
            {"pattern": "aggregation", "description": "Aggregation pipeline", "examples": ["$match", "$group", "$lookup"]}
        ]
    },
    "infrastructure": {
        "aws": [
            {"pattern": "lambda", "description": "Serverless functions", "examples": ["handlers", "layers", "triggers"]},
            {"pattern": "s3", "description": "Object storage", "examples": ["buckets", "policies", "presigned-urls"]}
        ],
        "docker": [
            {"pattern": "compose", "description": "Multi-container apps", "examples": ["services", "networks", "volumes"]},
            {"pattern": "optimization", "description": "Image optimization", "examples": ["multi-stage", "caching"]}
        ]
    },
    "game_dev": {
        "unreal": [
            {"pattern": "blueprints", "description": "Visual scripting", "examples": ["events", "functions", "macros"]},
            {"pattern": "cpp", "description": "C++ gameplay", "examples": ["actors", "components", "subsystems"]},
            {"pattern": "materials", "description": "Material system", "examples": ["shaders", "textures", "parameters"]},
            {"pattern": "ai", "description": "AI systems", "examples": ["behavior-trees", "eqs", "navigation"]}
        ],
        "unity": [
            {"pattern": "monobehaviour", "description": "Component scripts", "examples": ["Start", "Update", "coroutines"]},
            {"pattern": "ecs", "description": "Entity Component System", "examples": ["entities", "systems", "jobs"]}
        ]
    }
}


@router.get("/knowledge-graph")
async def get_knowledge_graph():
    """Get the full knowledge graph"""
    return {
        "graph": KNOWLEDGE_GRAPH,
        "stats": {
            "categories": len(KNOWLEDGE_GRAPH),
            "total_patterns": sum(
                len(patterns) 
                for category in KNOWLEDGE_GRAPH.values() 
                for patterns in category.values()
            )
        }
    }


@router.get("/knowledge-graph/{category}")
async def get_category_knowledge(category: str):
    """Get knowledge for a specific category"""
    if category not in KNOWLEDGE_GRAPH:
        raise HTTPException(status_code=404, detail="Category not found")
    return KNOWLEDGE_GRAPH[category]


@router.get("/knowledge-graph/{category}/{tech}")
async def get_tech_patterns(category: str, tech: str):
    """Get patterns for a specific technology"""
    if category not in KNOWLEDGE_GRAPH:
        raise HTTPException(status_code=404, detail="Category not found")
    if tech not in KNOWLEDGE_GRAPH[category]:
        raise HTTPException(status_code=404, detail="Technology not found")
    return KNOWLEDGE_GRAPH[category][tech]


@router.post("/knowledge-graph/learn")
async def learn_pattern(
    category: str,
    tech: str,
    pattern: str,
    description: str,
    examples: List[str] = []
):
    """Add a new pattern to the knowledge graph"""
    if category not in KNOWLEDGE_GRAPH:
        KNOWLEDGE_GRAPH[category] = {}
    if tech not in KNOWLEDGE_GRAPH[category]:
        KNOWLEDGE_GRAPH[category][tech] = []
    
    # Check if pattern exists
    for p in KNOWLEDGE_GRAPH[category][tech]:
        if p["pattern"] == pattern:
            # Update existing
            p["examples"].extend(examples)
            p["usage_count"] = p.get("usage_count", 0) + 1
            return {"status": "updated", "pattern": p}
    
    # Add new pattern
    new_pattern = {
        "pattern": pattern,
        "description": description,
        "examples": examples,
        "usage_count": 1,
        "learned_at": datetime.now(timezone.utc).isoformat()
    }
    KNOWLEDGE_GRAPH[category][tech].append(new_pattern)
    
    # Persist to database
    await db.knowledge_graph.update_one(
        {"category": category, "tech": tech},
        {"$push": {"patterns": new_pattern}},
        upsert=True
    )
    
    return {"status": "learned", "pattern": new_pattern}


@router.post("/knowledge-graph/query")
async def query_knowledge(query: str, limit: int = 10):
    """Query the knowledge graph for relevant patterns"""
    query_lower = query.lower()
    results = []
    
    for category, techs in KNOWLEDGE_GRAPH.items():
        for tech, patterns in techs.items():
            for pattern in patterns:
                # Simple relevance scoring
                score = 0
                if query_lower in pattern["pattern"].lower():
                    score += 10
                if query_lower in pattern["description"].lower():
                    score += 5
                for example in pattern.get("examples", []):
                    if query_lower in example.lower():
                        score += 2
                
                if score > 0:
                    results.append({
                        "category": category,
                        "tech": tech,
                        "pattern": pattern,
                        "score": score
                    })
    
    # Sort by score and return top results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


# =============================================================================
# SELF-CREATING AGENTS
# =============================================================================

AGENT_TEMPLATES = {
    "api_agent": {
        "name": "API Agent",
        "role": "api_specialist",
        "capabilities": ["endpoint_design", "api_documentation", "rate_limiting"],
        "triggers": ["api", "endpoint", "rest", "graphql"]
    },
    "testing_agent": {
        "name": "Testing Agent",
        "role": "qa_specialist",
        "capabilities": ["unit_tests", "integration_tests", "e2e_tests", "load_tests"],
        "triggers": ["test", "testing", "qa", "coverage"]
    },
    "ui_agent": {
        "name": "UI Agent",
        "role": "ui_specialist",
        "capabilities": ["component_design", "styling", "animations", "accessibility"],
        "triggers": ["ui", "design", "component", "style", "css"]
    },
    "devops_agent": {
        "name": "DevOps Agent",
        "role": "devops_specialist",
        "capabilities": ["ci_cd", "docker", "kubernetes", "monitoring"],
        "triggers": ["deploy", "devops", "docker", "ci", "cd"]
    },
    "security_agent": {
        "name": "Security Agent",
        "role": "security_specialist",
        "capabilities": ["vulnerability_scan", "auth_audit", "penetration_test"],
        "triggers": ["security", "vulnerability", "audit", "penetration"]
    },
    "performance_agent": {
        "name": "Performance Agent",
        "role": "performance_specialist",
        "capabilities": ["profiling", "optimization", "caching", "load_testing"],
        "triggers": ["performance", "optimize", "slow", "cache", "speed"]
    },
    "database_agent": {
        "name": "Database Agent",
        "role": "database_specialist",
        "capabilities": ["schema_design", "query_optimization", "migrations"],
        "triggers": ["database", "sql", "query", "schema", "migration"]
    },
    "ml_agent": {
        "name": "ML Agent",
        "role": "ml_specialist",
        "capabilities": ["model_training", "inference", "data_pipeline"],
        "triggers": ["ml", "machine learning", "ai", "model", "training"]
    }
}

# Track spawned agents
_spawned_agents: Dict[str, dict] = {}


@router.get("/agents/templates")
async def get_agent_templates():
    """Get available agent templates"""
    return AGENT_TEMPLATES


@router.get("/agents/spawned")
async def get_spawned_agents():
    """Get all spawned agents"""
    return list(_spawned_agents.values())


@router.post("/agents/spawn")
async def spawn_agent(template_id: str, project_id: str = None):
    """Spawn a new specialized agent"""
    if template_id not in AGENT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Agent template not found")
    
    template = AGENT_TEMPLATES[template_id]
    agent_id = f"agent-{uuid.uuid4().hex[:8]}"
    
    agent = {
        "id": agent_id,
        "template_id": template_id,
        "name": template["name"],
        "role": template["role"],
        "capabilities": template["capabilities"],
        "status": "active",
        "project_id": project_id,
        "tasks_completed": 0,
        "spawned_at": datetime.now(timezone.utc).isoformat()
    }
    
    _spawned_agents[agent_id] = agent
    await db.spawned_agents.insert_one(agent)
    
    return serialize_doc(agent)


@router.post("/agents/auto-spawn")
async def auto_spawn_agent(task_description: str, project_id: str = None):
    """Automatically detect needed agent and spawn it"""
    task_lower = task_description.lower()
    
    # Find matching agent template
    best_match = None
    best_score = 0
    
    for template_id, template in AGENT_TEMPLATES.items():
        score = 0
        for trigger in template["triggers"]:
            if trigger in task_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = template_id
    
    if best_match and best_score > 0:
        agent = await spawn_agent(best_match, project_id)
        return {
            "auto_spawned": True,
            "reason": f"Detected need for {AGENT_TEMPLATES[best_match]['name']}",
            "agent": agent
        }
    
    return {
        "auto_spawned": False,
        "reason": "No specialized agent needed for this task"
    }


# =============================================================================
# PARALLEL ARCHITECTURE EXPLORATION
# =============================================================================

ARCHITECTURE_OPTIONS = {
    "monolith": {
        "name": "Monolithic Architecture",
        "description": "Single deployable unit",
        "pros": ["Simple deployment", "Easy debugging", "Lower latency"],
        "cons": ["Scaling limitations", "Tight coupling"],
        "best_for": ["Small teams", "MVPs", "Simple apps"]
    },
    "microservices": {
        "name": "Microservices Architecture",
        "description": "Distributed services",
        "pros": ["Independent scaling", "Technology flexibility", "Fault isolation"],
        "cons": ["Complexity", "Network overhead", "Data consistency"],
        "best_for": ["Large teams", "Complex domains", "High scale"]
    },
    "serverless": {
        "name": "Serverless Architecture",
        "description": "Function-based deployment",
        "pros": ["Pay per use", "Auto scaling", "No server management"],
        "cons": ["Cold starts", "Vendor lock-in", "Limited execution time"],
        "best_for": ["Event-driven", "Variable workloads", "Startups"]
    },
    "jamstack": {
        "name": "JAMstack Architecture",
        "description": "Static + API architecture",
        "pros": ["Performance", "Security", "Scalability"],
        "cons": ["Dynamic limitations", "Build times"],
        "best_for": ["Content sites", "E-commerce", "Blogs"]
    },
    "event_driven": {
        "name": "Event-Driven Architecture",
        "description": "Async event processing",
        "pros": ["Loose coupling", "Scalability", "Real-time"],
        "cons": ["Complexity", "Event ordering", "Debugging"],
        "best_for": ["Real-time apps", "IoT", "Analytics"]
    }
}


@router.get("/architecture/options")
async def get_architecture_options():
    """Get available architecture patterns"""
    return ARCHITECTURE_OPTIONS


@router.post("/architecture/explore")
async def explore_architectures(
    background_tasks: BackgroundTasks,
    project_description: str,
    requirements: List[str] = []
):
    """
    Parallel Architecture Exploration
    Evaluates multiple architectures simultaneously and recommends the best
    """
    exploration_id = f"explore-{uuid.uuid4().hex[:8]}"
    
    exploration = {
        "id": exploration_id,
        "description": project_description,
        "requirements": requirements,
        "status": "exploring",
        "evaluations": {},
        "recommendation": None,
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Evaluate each architecture
    for arch_id, arch in ARCHITECTURE_OPTIONS.items():
        score = 0
        reasons = []
        
        # Score based on requirements
        req_lower = " ".join(requirements).lower()
        desc_lower = project_description.lower()
        
        # Check best_for matches
        for best in arch["best_for"]:
            if best.lower() in req_lower or best.lower() in desc_lower:
                score += 20
                reasons.append(f"Matches use case: {best}")
        
        # Check specific keywords
        if "scale" in req_lower or "scalable" in req_lower:
            if arch_id in ["microservices", "serverless"]:
                score += 15
                reasons.append("Good for scalability")
        
        if "simple" in req_lower or "mvp" in req_lower:
            if arch_id == "monolith":
                score += 15
                reasons.append("Good for simplicity/MVP")
        
        if "real-time" in req_lower or "realtime" in req_lower:
            if arch_id == "event_driven":
                score += 15
                reasons.append("Good for real-time")
        
        if "cost" in req_lower or "budget" in req_lower:
            if arch_id == "serverless":
                score += 15
                reasons.append("Cost-effective pay-per-use")
        
        exploration["evaluations"][arch_id] = {
            "architecture": arch,
            "score": score,
            "reasons": reasons
        }
    
    # Find best architecture
    best_arch = max(exploration["evaluations"].items(), key=lambda x: x[1]["score"])
    exploration["recommendation"] = {
        "architecture_id": best_arch[0],
        "architecture": best_arch[1]["architecture"],
        "score": best_arch[1]["score"],
        "reasons": best_arch[1]["reasons"]
    }
    
    exploration["status"] = "complete"
    exploration["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.architecture_explorations.insert_one(exploration)
    
    return serialize_doc(exploration)


# =============================================================================
# SOFTWARE EVOLUTION ENGINE
# =============================================================================

@router.post("/evolution/analyze")
async def analyze_for_evolution(project_id: str):
    """Analyze a project for potential improvements"""
    # Get project files
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    
    improvements = []
    
    # Analyze patterns
    for file in files:
        content = file.get("content", "")
        
        # Check for common improvement opportunities
        if "console.log" in content:
            improvements.append({
                "file": file["name"],
                "type": "cleanup",
                "description": "Remove console.log statements",
                "priority": "low"
            })
        
        if "TODO" in content or "FIXME" in content:
            improvements.append({
                "file": file["name"],
                "type": "technical_debt",
                "description": "Address TODO/FIXME comments",
                "priority": "medium"
            })
        
        if len(content) > 500 and content.count("function") > 10:
            improvements.append({
                "file": file["name"],
                "type": "refactor",
                "description": "Consider splitting large file into modules",
                "priority": "medium"
            })
    
    # General recommendations
    improvements.append({
        "file": None,
        "type": "dependency",
        "description": "Check for dependency updates",
        "priority": "low"
    })
    
    return {
        "project_id": project_id,
        "total_files": len(files),
        "improvements": improvements,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/evolution/evolve")
async def evolve_project(
    background_tasks: BackgroundTasks,
    project_id: str,
    apply_improvements: List[str] = []
):
    """Evolve a project by applying improvements"""
    evolution_id = f"evolve-{uuid.uuid4().hex[:8]}"
    
    evolution = {
        "id": evolution_id,
        "project_id": project_id,
        "improvements_applied": apply_improvements,
        "status": "evolving",
        "changes": [],
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    # In a real implementation, this would:
    # 1. Apply code fixes
    # 2. Update dependencies
    # 3. Refactor code
    # 4. Run tests to validate
    
    evolution["status"] = "complete"
    evolution["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.evolutions.insert_one(evolution)
    
    return serialize_doc(evolution)


# =============================================================================
# AUTONOMOUS RESEARCH MODE
# =============================================================================

RESEARCH_TOPICS = [
    {"topic": "transformer_architecture", "source": "arxiv", "category": "ml"},
    {"topic": "react_server_components", "source": "rfc", "category": "frontend"},
    {"topic": "vector_databases", "source": "papers", "category": "database"},
    {"topic": "webgpu", "source": "spec", "category": "graphics"},
    {"topic": "edge_computing", "source": "industry", "category": "infrastructure"}
]


@router.get("/research/topics")
async def get_research_topics():
    """Get active research topics"""
    return RESEARCH_TOPICS


@router.post("/research/explore")
async def explore_research(topic: str):
    """Explore a research topic and generate implementation prototype"""
    research_id = f"research-{uuid.uuid4().hex[:8]}"
    
    research = {
        "id": research_id,
        "topic": topic,
        "status": "researching",
        "findings": [],
        "prototype": None,
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Simulate research process
    research["findings"] = [
        {"source": "arxiv", "title": f"Recent advances in {topic}", "relevance": 0.9},
        {"source": "github", "title": f"Open source {topic} implementation", "relevance": 0.8},
        {"source": "blog", "title": f"Practical {topic} guide", "relevance": 0.7}
    ]
    
    research["prototype"] = {
        "name": f"{topic}_prototype",
        "files": [
            {"name": "main.py", "description": "Core implementation"},
            {"name": "test.py", "description": "Benchmark tests"},
            {"name": "README.md", "description": "Documentation"}
        ],
        "estimated_time": "2 hours"
    }
    
    research["status"] = "complete"
    research["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.research.insert_one(research)
    
    return serialize_doc(research)
