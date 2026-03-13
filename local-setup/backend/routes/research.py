"""
Research Mode - arXiv, PapersWithCode, HuggingFace integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from core.database import db
import uuid
import httpx

router = APIRouter(prefix="/research", tags=["research"])

class SearchRequest(BaseModel):
    query: str
    source: str = "arxiv"  # arxiv, paperswithcode, huggingface
    max_results: int = 10

class PrototypeRequest(BaseModel):
    paper_id: str
    source: str
    title: str
    framework: str = "pytorch"

@router.get("/sources")
async def get_sources():
    """Get available research sources"""
    return {
        "arxiv": {
            "name": "arXiv",
            "description": "Open-access archive for scholarly articles",
            "categories": ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE"]
        },
        "paperswithcode": {
            "name": "Papers With Code",
            "description": "Machine learning papers with code implementations",
            "features": ["benchmarks", "datasets", "methods"]
        },
        "huggingface": {
            "name": "HuggingFace",
            "description": "AI models and datasets hub",
            "features": ["models", "datasets", "spaces"]
        }
    }

@router.post("/search")
async def search_papers(request: SearchRequest):
    """Search research papers"""
    
    if request.source == "arxiv":
        return await search_arxiv(request.query, request.max_results)
    elif request.source == "paperswithcode":
        return await search_paperswithcode(request.query, request.max_results)
    elif request.source == "huggingface":
        return await search_huggingface(request.query, request.max_results)
    else:
        raise HTTPException(status_code=400, detail="Invalid source")

async def search_arxiv(query: str, max_results: int):
    """Search arXiv papers"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://export.arxiv.org/api/query",
                params={
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "relevance"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                papers = []
                ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
                
                for entry in root.findall("atom:entry", ns):
                    title = entry.find("atom:title", ns)
                    summary = entry.find("atom:summary", ns)
                    arxiv_id = entry.find("atom:id", ns)
                    published = entry.find("atom:published", ns)
                    
                    authors = []
                    for author in entry.findall("atom:author", ns):
                        name = author.find("atom:name", ns)
                        if name is not None:
                            authors.append(name.text)
                    
                    papers.append({
                        "id": arxiv_id.text.split("/")[-1] if arxiv_id is not None else "",
                        "title": title.text.strip() if title is not None else "",
                        "summary": summary.text.strip()[:500] if summary is not None else "",
                        "authors": authors[:5],
                        "published": published.text if published is not None else "",
                        "source": "arxiv",
                        "url": arxiv_id.text if arxiv_id is not None else ""
                    })
                
                return {"source": "arxiv", "query": query, "results": papers}
    except Exception as e:
        return {"source": "arxiv", "query": query, "results": [], "error": str(e)}

async def search_paperswithcode(query: str, max_results: int):
    """Search Papers With Code"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://paperswithcode.com/api/v1/papers/",
                params={"q": query, "page": 1, "items_per_page": max_results},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for paper in data.get("results", []):
                    papers.append({
                        "id": paper.get("id", ""),
                        "title": paper.get("title", ""),
                        "summary": paper.get("abstract", "")[:500],
                        "authors": paper.get("authors", [])[:5],
                        "published": paper.get("published", ""),
                        "source": "paperswithcode",
                        "url": paper.get("url_abs", ""),
                        "has_code": paper.get("proceeding", None) is not None
                    })
                
                return {"source": "paperswithcode", "query": query, "results": papers}
    except Exception as e:
        return {"source": "paperswithcode", "query": query, "results": [], "error": str(e)}

async def search_huggingface(query: str, max_results: int):
    """Search HuggingFace models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://huggingface.co/api/models",
                params={"search": query, "limit": max_results, "sort": "downloads", "direction": -1},
                timeout=30.0
            )
            
            if response.status_code == 200:
                models = response.json()
                results = []
                
                for model in models:
                    results.append({
                        "id": model.get("modelId", ""),
                        "title": model.get("modelId", "").split("/")[-1],
                        "summary": model.get("description", "")[:500] if model.get("description") else "",
                        "authors": [model.get("author", "")],
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "source": "huggingface",
                        "url": f"https://huggingface.co/{model.get('modelId', '')}",
                        "pipeline_tag": model.get("pipeline_tag", "")
                    })
                
                return {"source": "huggingface", "query": query, "results": results}
    except Exception as e:
        return {"source": "huggingface", "query": query, "results": [], "error": str(e)}

@router.post("/prototype")
async def create_prototype(request: PrototypeRequest):
    """Create a prototype from a research paper"""
    
    prototype_id = str(uuid.uuid4())
    
    prototype = {
        "id": prototype_id,
        "paper_id": request.paper_id,
        "source": request.source,
        "title": request.title,
        "framework": request.framework,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code": generate_prototype_code(request.title, request.framework)
    }
    
    await db.research_prototypes.insert_one(prototype)
    
    return {"prototype_id": prototype_id, "status": "created"}

def generate_prototype_code(title: str, framework: str) -> str:
    """Generate starter prototype code"""
    
    if framework == "pytorch":
        return f'''# Prototype: {title}
# Generated by AgentForge Research Mode

import torch
import torch.nn as nn

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        # TODO: Implement architecture from paper
        self.layers = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        return self.layers(x)

if __name__ == "__main__":
    model = Model()
    print(f"Model parameters: {{sum(p.numel() for p in model.parameters())}}")
'''
    elif framework == "tensorflow":
        return f'''# Prototype: {title}
# Generated by AgentForge Research Mode

import tensorflow as tf
from tensorflow import keras

def create_model():
    # TODO: Implement architecture from paper
    model = keras.Sequential([
        keras.layers.Dense(256, activation='relu', input_shape=(512,)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax')
    ])
    return model

if __name__ == "__main__":
    model = create_model()
    model.summary()
'''
    else:
        return f"# Prototype: {title}\n# Framework: {framework}\n# TODO: Implement"

@router.get("/prototypes")
async def list_prototypes():
    """List all prototypes"""
    prototypes = await db.research_prototypes.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return prototypes

@router.get("/prototypes/{prototype_id}")
async def get_prototype(prototype_id: str):
    """Get prototype details"""
    prototype = await db.research_prototypes.find_one({"id": prototype_id}, {"_id": 0})
    if not prototype:
        raise HTTPException(status_code=404, detail="Prototype not found")
    return prototype
