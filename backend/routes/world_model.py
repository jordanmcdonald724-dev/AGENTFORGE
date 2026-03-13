"""
World Model - Systems Graph
===========================
Global knowledge graph that learns from every project.
Agents query learned patterns for intelligent decision-making.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json

router = APIRouter(prefix="/world-model", tags=["world-model"])


# ========== SYSTEMS GRAPH ==========

SYSTEM_CATEGORIES = {
    "frontend": {
        "react": ["routing", "state-management", "auth-patterns", "hooks", "context", "redux", "zustand"],
        "vue": ["composition-api", "vuex", "pinia", "routing"],
        "angular": ["services", "modules", "rxjs", "ngrx"],
        "svelte": ["stores", "actions", "transitions"]
    },
    "backend": {
        "node": ["express", "fastify", "auth", "database", "caching", "websockets"],
        "python": ["fastapi", "django", "flask", "sqlalchemy", "async"],
        "go": ["gin", "fiber", "grpc", "concurrency"],
        "rust": ["actix", "axum", "tokio"]
    },
    "game_engines": {
        "unreal": ["blueprints", "physics", "water-system", "ai-controller", "multiplayer", "niagara", "nanite"],
        "unity": ["mono", "dots", "physics", "networking", "ui-toolkit"],
        "godot": ["gdscript", "signals", "scenes", "physics-2d", "physics-3d"]
    },
    "infrastructure": {
        "database": ["postgres", "mongodb", "redis", "elasticsearch"],
        "cloud": ["aws", "gcp", "azure", "vercel", "railway"],
        "devops": ["docker", "kubernetes", "ci-cd", "monitoring"]
    },
    "ai_ml": {
        "llm": ["openai", "anthropic", "local-models", "rag", "embeddings"],
        "vision": ["object-detection", "segmentation", "generation"],
        "audio": ["tts", "stt", "music-generation"]
    }
}


@router.get("/categories")
async def get_system_categories():
    """Get all system categories in the world model"""
    return SYSTEM_CATEGORIES


@router.get("/graph")
async def get_systems_graph():
    """Get the full systems knowledge graph"""
    nodes = await db.world_model_nodes.find({}, {"_id": 0}).to_list(1000)
    edges = await db.world_model_edges.find({}, {"_id": 0}).to_list(5000)
    
    # Add base categories as nodes if empty
    if not nodes:
        nodes = []
        for category, systems in SYSTEM_CATEGORIES.items():
            cat_node = {
                "id": f"cat-{category}",
                "type": "category",
                "name": category.replace("_", " ").title(),
                "level": 0
            }
            nodes.append(cat_node)
            
            for system, patterns in systems.items():
                sys_node = {
                    "id": f"sys-{system}",
                    "type": "system",
                    "name": system.title(),
                    "parent": cat_node["id"],
                    "level": 1
                }
                nodes.append(sys_node)
                edges.append({"source": cat_node["id"], "target": sys_node["id"], "type": "contains"})
                
                for pattern in patterns:
                    pat_node = {
                        "id": f"pat-{system}-{pattern}",
                        "type": "pattern",
                        "name": pattern.replace("-", " ").title(),
                        "parent": sys_node["id"],
                        "level": 2
                    }
                    nodes.append(pat_node)
                    edges.append({"source": sys_node["id"], "target": pat_node["id"], "type": "has_pattern"})
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "categories": len(SYSTEM_CATEGORIES),
            "learned_patterns": await db.learned_patterns.count_documents({})
        }
    }


@router.post("/learn")
async def learn_from_project(project_id: str):
    """Extract and learn patterns from a project"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    # Analyze project structure
    patterns_found = []
    tech_stack = set()
    
    for f in files:
        filepath = f.get("filepath", "").lower()
        content = f.get("content", "")
        
        # Detect technologies
        if "react" in content or "jsx" in filepath:
            tech_stack.add("react")
        if "fastapi" in content or "uvicorn" in content:
            tech_stack.add("fastapi")
        if "express" in content:
            tech_stack.add("express")
        if "unreal" in content.lower() or ".cpp" in filepath:
            tech_stack.add("unreal")
        if "unity" in content.lower() or ".cs" in filepath:
            tech_stack.add("unity")
        if "mongodb" in content or "mongoose" in content:
            tech_stack.add("mongodb")
        if "postgres" in content or "psycopg" in content:
            tech_stack.add("postgres")
        
        # Detect patterns
        if "usestate" in content.lower() or "useeffect" in content.lower():
            patterns_found.append({"type": "react-hooks", "file": filepath})
        if "redux" in content.lower():
            patterns_found.append({"type": "redux", "file": filepath})
        if "jwt" in content.lower() or "bearer" in content.lower():
            patterns_found.append({"type": "jwt-auth", "file": filepath})
        if "websocket" in content.lower():
            patterns_found.append({"type": "websockets", "file": filepath})
        if "async def" in content or "await" in content:
            patterns_found.append({"type": "async-patterns", "file": filepath})
    
    # Store learned knowledge
    knowledge_entry = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "project_name": project.get("name"),
        "project_type": project.get("type"),
        "tech_stack": list(tech_stack),
        "patterns_found": patterns_found,
        "file_count": len(files),
        "learned_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.learned_patterns.insert_one(knowledge_entry)
    
    # Update graph nodes with usage counts
    for tech in tech_stack:
        await db.world_model_nodes.update_one(
            {"id": f"sys-{tech}"},
            {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
    
    return serialize_doc(knowledge_entry)


@router.get("/query")
async def query_world_model(question: str):
    """Query the world model for best practices"""
    # Get learned patterns
    patterns = await db.learned_patterns.find({}, {"_id": 0}).to_list(100)
    
    # Build context from world model
    context_parts = ["WORLD MODEL KNOWLEDGE:"]
    
    tech_usage = {}
    pattern_usage = {}
    
    for p in patterns:
        for tech in p.get("tech_stack", []):
            tech_usage[tech] = tech_usage.get(tech, 0) + 1
        for pat in p.get("patterns_found", []):
            pat_type = pat.get("type", "")
            pattern_usage[pat_type] = pattern_usage.get(pat_type, 0) + 1
    
    if tech_usage:
        context_parts.append(f"\nMost used technologies: {sorted(tech_usage.items(), key=lambda x: -x[1])[:10]}")
    if pattern_usage:
        context_parts.append(f"\nCommon patterns: {sorted(pattern_usage.items(), key=lambda x: -x[1])[:10]}")
    context_parts.append(f"\nTotal projects analyzed: {len(patterns)}")
    
    context = "\n".join(context_parts)
    
    # Query LLM with world model context
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": f"""You are Atlas, the Architecture Agent for AgentForge.
You have access to a World Model - a knowledge graph built from analyzing many software projects.

{context}

Use this knowledge to provide data-driven architectural recommendations.
Reference specific patterns and technologies that have proven successful."""},
                {"role": "user", "content": question}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Query failed: {str(e)}"
    
    return {
        "question": question,
        "answer": answer,
        "context_used": {
            "tech_usage": tech_usage,
            "pattern_usage": pattern_usage,
            "projects_analyzed": len(patterns)
        }
    }


@router.get("/insights")
async def get_world_model_insights():
    """Get insights and statistics from the world model"""
    patterns = await db.learned_patterns.find({}, {"_id": 0}).to_list(500)
    
    tech_stats = {}
    pattern_stats = {}
    project_types = {}
    
    for p in patterns:
        # Tech usage
        for tech in p.get("tech_stack", []):
            tech_stats[tech] = tech_stats.get(tech, 0) + 1
        
        # Pattern usage
        for pat in p.get("patterns_found", []):
            pat_type = pat.get("type", "unknown")
            pattern_stats[pat_type] = pattern_stats.get(pat_type, 0) + 1
        
        # Project types
        ptype = p.get("project_type", "unknown")
        project_types[ptype] = project_types.get(ptype, 0) + 1
    
    return {
        "total_projects_analyzed": len(patterns),
        "top_technologies": sorted(tech_stats.items(), key=lambda x: -x[1])[:15],
        "top_patterns": sorted(pattern_stats.items(), key=lambda x: -x[1])[:15],
        "project_types": project_types,
        "recommendations": _generate_recommendations(tech_stats, pattern_stats)
    }


def _generate_recommendations(tech_stats: dict, pattern_stats: dict) -> List[str]:
    """Generate recommendations based on world model data"""
    recs = []
    
    if tech_stats.get("react", 0) > tech_stats.get("vue", 0):
        recs.append("React is the most successful frontend framework in your projects")
    
    if pattern_stats.get("jwt-auth", 0) > 3:
        recs.append("JWT authentication is a proven pattern - consider reusing existing implementations")
    
    if pattern_stats.get("websockets", 0) > 2:
        recs.append("WebSocket patterns are commonly used - consider extracting as reusable module")
    
    if tech_stats.get("fastapi", 0) > tech_stats.get("express", 0):
        recs.append("FastAPI has shown better results than Express in your projects")
    
    return recs


@router.post("/nodes")
async def add_knowledge_node(
    name: str,
    node_type: str,
    parent_id: str = None,
    metadata: dict = None
):
    """Manually add a node to the world model"""
    node = {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": node_type,
        "parent_id": parent_id,
        "metadata": metadata or {},
        "usage_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.world_model_nodes.insert_one(node)
    
    if parent_id:
        await db.world_model_edges.insert_one({
            "source": parent_id,
            "target": node["id"],
            "type": "contains"
        })
    
    return serialize_doc(node)


@router.delete("/nodes/{node_id}")
async def delete_knowledge_node(node_id: str):
    """Remove a node from the world model"""
    await db.world_model_nodes.delete_one({"id": node_id})
    await db.world_model_edges.delete_many({"$or": [{"source": node_id}, {"target": node_id}]})
    return {"success": True}
