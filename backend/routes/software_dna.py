"""
Software DNA - Genes System
===========================
Reusable building blocks extracted from every build.
Projects become evolutionary through genome assembly.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json
import hashlib

router = APIRouter(prefix="/dna", tags=["software-dna"])


# ========== GENE TEMPLATES ==========

GENE_CATEGORIES = {
    "auth": {
        "name": "Authentication",
        "icon": "shield",
        "genes": ["jwt-auth", "oauth2", "session-auth", "api-keys", "rbac", "2fa"]
    },
    "ui": {
        "name": "UI Components",
        "icon": "layout",
        "genes": ["dashboard", "forms", "tables", "modals", "navigation", "charts"]
    },
    "data": {
        "name": "Data Layer",
        "icon": "database",
        "genes": ["crud-api", "caching", "search", "pagination", "file-upload", "realtime"]
    },
    "game": {
        "name": "Game Systems",
        "icon": "gamepad",
        "genes": ["player-controller", "inventory", "save-system", "ai-npc", "physics", "multiplayer"]
    },
    "infra": {
        "name": "Infrastructure",
        "icon": "server",
        "genes": ["docker", "ci-cd", "monitoring", "logging", "rate-limiting", "queue"]
    },
    "ai": {
        "name": "AI/ML",
        "icon": "brain",
        "genes": ["llm-integration", "embeddings", "rag", "image-gen", "speech", "agents"]
    }
}


@router.get("/categories")
async def get_gene_categories():
    """Get all gene categories"""
    return GENE_CATEGORIES


@router.get("/library")
async def get_gene_library():
    """Get the full gene library"""
    genes = await db.genes.find({}, {"_id": 0}).to_list(500)
    
    # Group by category
    library = {cat: [] for cat in GENE_CATEGORIES.keys()}
    
    for gene in genes:
        cat = gene.get("category", "misc")
        if cat in library:
            library[cat].append(gene)
    
    return {
        "categories": GENE_CATEGORIES,
        "genes": library,
        "total_genes": len(genes),
        "stats": {
            "most_used": await _get_most_used_genes(),
            "recently_added": await _get_recent_genes()
        }
    }


async def _get_most_used_genes():
    """Get most frequently used genes"""
    genes = await db.genes.find({}, {"_id": 0}).sort("usage_count", -1).to_list(10)
    return [{"name": g["name"], "usage": g.get("usage_count", 0)} for g in genes]


async def _get_recent_genes():
    """Get recently added genes"""
    genes = await db.genes.find({}, {"_id": 0}).sort("created_at", -1).to_list(5)
    return [{"name": g["name"], "created": g.get("created_at")} for g in genes]


@router.post("/extract")
async def extract_genes_from_project(project_id: str):
    """Extract reusable genes from a project"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    extracted_genes = []
    
    for f in files:
        filepath = f.get("filepath", "").lower()
        content = f.get("content", "")
        
        # Detect gene patterns
        if "auth" in filepath or "login" in filepath or "jwt" in content.lower():
            gene = await _create_or_update_gene(
                name="Authentication Module",
                category="auth",
                gene_type="jwt-auth",
                source_file=filepath,
                source_project=project_id,
                code_snippet=content[:2000]
            )
            extracted_genes.append(gene)
        
        if "crud" in filepath or ("create" in content and "read" in content and "update" in content):
            gene = await _create_or_update_gene(
                name="CRUD API",
                category="data",
                gene_type="crud-api",
                source_file=filepath,
                source_project=project_id,
                code_snippet=content[:2000]
            )
            extracted_genes.append(gene)
        
        if "player" in filepath.lower() or "controller" in filepath.lower():
            gene = await _create_or_update_gene(
                name="Player Controller",
                category="game",
                gene_type="player-controller",
                source_file=filepath,
                source_project=project_id,
                code_snippet=content[:2000]
            )
            extracted_genes.append(gene)
        
        if "inventory" in filepath.lower():
            gene = await _create_or_update_gene(
                name="Inventory System",
                category="game",
                gene_type="inventory",
                source_file=filepath,
                source_project=project_id,
                code_snippet=content[:2000]
            )
            extracted_genes.append(gene)
        
        if "dashboard" in filepath.lower():
            gene = await _create_or_update_gene(
                name="Dashboard UI",
                category="ui",
                gene_type="dashboard",
                source_file=filepath,
                source_project=project_id,
                code_snippet=content[:2000]
            )
            extracted_genes.append(gene)
        
        if "llm" in content.lower() or "openai" in content.lower() or "anthropic" in content.lower():
            gene = await _create_or_update_gene(
                name="LLM Integration",
                category="ai",
                gene_type="llm-integration",
                source_file=filepath,
                source_project=project_id,
                code_snippet=content[:2000]
            )
            extracted_genes.append(gene)
    
    return {
        "project_id": project_id,
        "genes_extracted": len(extracted_genes),
        "genes": extracted_genes
    }


async def _create_or_update_gene(name: str, category: str, gene_type: str, 
                                  source_file: str, source_project: str, code_snippet: str):
    """Create or update a gene in the library"""
    # Generate hash for deduplication
    code_hash = hashlib.md5(code_snippet.encode()).hexdigest()[:12]
    
    existing = await db.genes.find_one({"gene_type": gene_type, "code_hash": code_hash})
    
    if existing:
        await db.genes.update_one(
            {"id": existing["id"]},
            {"$inc": {"usage_count": 1}, "$push": {"source_projects": source_project}}
        )
        return {"id": existing["id"], "name": name, "status": "updated"}
    
    gene = {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "gene_type": gene_type,
        "code_hash": code_hash,
        "code_snippet": code_snippet,
        "source_file": source_file,
        "source_projects": [source_project],
        "usage_count": 1,
        "quality_score": 0.7,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.genes.insert_one(gene)
    return {"id": gene["id"], "name": name, "status": "created"}


@router.get("/{gene_id}")
async def get_gene(gene_id: str):
    """Get a specific gene"""
    gene = await db.genes.find_one({"id": gene_id}, {"_id": 0})
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")
    return gene


@router.delete("/{gene_id}")
async def delete_gene(gene_id: str):
    """Delete a gene from the library"""
    await db.genes.delete_one({"id": gene_id})
    return {"success": True}


# ========== GENOME ASSEMBLY ==========

@router.post("/genome/create")
async def create_genome(
    name: str,
    description: str,
    gene_ids: List[str],
    target_engine: str = "web"
):
    """Create a project genome from selected genes"""
    genes = await db.genes.find({"id": {"$in": gene_ids}}, {"_id": 0}).to_list(50)
    
    if len(genes) != len(gene_ids):
        raise HTTPException(status_code=400, detail="Some genes not found")
    
    genome = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "genes": [{"id": g["id"], "name": g["name"], "category": g["category"]} for g in genes],
        "target_engine": target_engine,
        "compatibility_score": _calculate_compatibility(genes),
        "estimated_files": sum(1 for g in genes),
        "status": "ready",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.genomes.insert_one(genome)
    return serialize_doc(genome)


def _calculate_compatibility(genes: List[dict]) -> float:
    """Calculate how well genes work together"""
    # Simple compatibility scoring
    categories = [g.get("category") for g in genes]
    unique_categories = len(set(categories))
    
    # More diverse = higher compatibility potential
    return min(1.0, 0.5 + (unique_categories * 0.1))


@router.get("/genome/{genome_id}")
async def get_genome(genome_id: str):
    """Get a specific genome"""
    genome = await db.genomes.find_one({"id": genome_id}, {"_id": 0})
    if not genome:
        raise HTTPException(status_code=404, detail="Genome not found")
    return genome


@router.get("/genomes")
async def list_genomes():
    """List all genomes"""
    return await db.genomes.find({}, {"_id": 0}).to_list(100)


@router.post("/genome/{genome_id}/instantiate")
async def instantiate_genome(genome_id: str, project_name: str):
    """Create a new project from a genome"""
    genome = await db.genomes.find_one({"id": genome_id}, {"_id": 0})
    if not genome:
        raise HTTPException(status_code=404, detail="Genome not found")
    
    # Create project
    project = {
        "id": str(uuid.uuid4()),
        "name": project_name,
        "type": genome.get("target_engine", "web_app"),
        "description": f"Generated from genome: {genome['name']}",
        "status": "active",
        "source_genome_id": genome_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.projects.insert_one(project)
    
    # Increment usage count for genes
    gene_ids = [g["id"] for g in genome.get("genes", [])]
    await db.genes.update_many(
        {"id": {"$in": gene_ids}},
        {"$inc": {"usage_count": 1}}
    )
    
    return {
        "project": serialize_doc(project),
        "genome": genome["name"],
        "genes_used": len(gene_ids)
    }


# ========== EVOLUTION ==========

@router.post("/evolve")
async def evolve_genes(gene_ids: List[str], mutation_type: str = "optimize"):
    """Evolve genes through AI-powered optimization"""
    genes = await db.genes.find({"id": {"$in": gene_ids}}, {"_id": 0}).to_list(10)
    
    if not genes:
        raise HTTPException(status_code=404, detail="Genes not found")
    
    # Use LLM to suggest improvements
    gene_summaries = "\n".join([
        f"- {g['name']} ({g['category']}): {g.get('code_snippet', '')[:500]}"
        for g in genes
    ])
    
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """You are a code evolution specialist.
Analyze the provided code genes and suggest improvements for better:
- Performance
- Maintainability
- Reusability
- Modern best practices

Provide specific code improvements."""},
                {"role": "user", "content": f"Evolve these genes ({mutation_type}):\n{gene_summaries}"}
            ],
            max_tokens=4000
        )
        evolution_suggestions = response.choices[0].message.content
    except Exception as e:
        evolution_suggestions = f"Evolution analysis failed: {str(e)}"
    
    return {
        "genes_analyzed": len(genes),
        "mutation_type": mutation_type,
        "evolution_suggestions": evolution_suggestions
    }
