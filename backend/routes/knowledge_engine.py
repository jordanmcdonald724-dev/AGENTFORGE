"""
Knowledge Engine (AI Research Layer)
====================================
Integration with ArXiv and research sources.
Read new research → Extract algorithms → Implement prototypes automatically.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import httpx

router = APIRouter(prefix="/knowledge-engine", tags=["knowledge-engine"])


RESEARCH_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.LG": "Machine Learning",
    "cs.CV": "Computer Vision",
    "cs.CL": "Computation and Language (NLP)",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.RO": "Robotics",
    "cs.GR": "Graphics",
    "cs.GT": "Game Theory",
    "cs.SE": "Software Engineering"
}


@router.get("/categories")
async def get_research_categories():
    """Get available research categories"""
    return RESEARCH_CATEGORIES


@router.post("/search")
async def search_papers(
    query: str,
    category: str = "cs.AI",
    max_results: int = 10
):
    """Search for research papers on ArXiv"""
    
    search_result = {
        "id": str(uuid.uuid4()),
        "query": query,
        "category": category,
        "papers": [],
        "searched_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Query ArXiv API
            response = await client.get(
                "http://export.arxiv.org/api/query",
                params={
                    "search_query": f"all:{query} AND cat:{category}",
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                
                for entry in root.findall("atom:entry", ns):
                    paper = {
                        "id": entry.find("atom:id", ns).text if entry.find("atom:id", ns) is not None else "",
                        "title": entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else "",
                        "summary": entry.find("atom:summary", ns).text.strip()[:500] if entry.find("atom:summary", ns) is not None else "",
                        "authors": [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns) if a.find("atom:name", ns) is not None][:5],
                        "published": entry.find("atom:published", ns).text if entry.find("atom:published", ns) is not None else "",
                        "pdf_url": ""
                    }
                    
                    for link in entry.findall("atom:link", ns):
                        if link.get("title") == "pdf":
                            paper["pdf_url"] = link.get("href", "")
                    
                    search_result["papers"].append(paper)
                    
    except Exception as e:
        search_result["error"] = str(e)
    
    await db.research_searches.insert_one(search_result)
    return serialize_doc(search_result)


@router.post("/analyze")
async def analyze_paper(paper_id: str = None, paper_url: str = None, abstract: str = None):
    """Analyze a research paper and extract key algorithms"""
    
    analysis = {
        "id": str(uuid.uuid4()),
        "paper_id": paper_id,
        "paper_url": paper_url,
        "status": "analyzing",
        "algorithms": [],
        "key_findings": [],
        "implementation_notes": [],
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Use abstract or fetch paper content
    content = abstract or f"Paper ID: {paper_id}"
    
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """Analyze this research paper and extract:
1. Key algorithms and their descriptions
2. Main findings and contributions
3. Implementation notes and pseudocode

Output JSON:
{
    "algorithms": [{"name": "...", "description": "...", "pseudocode": "..."}],
    "key_findings": ["finding1", "finding2"],
    "implementation_notes": ["note1", "note2"],
    "complexity": "O(n) or similar",
    "dependencies": ["library1", "library2"],
    "applicability": "What problems this solves"
}"""},
                {"role": "user", "content": f"Analyze this paper:\n{content}"}
            ],
            max_tokens=3000
        )
        
        import json
        import re
        result_text = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        
        if json_match:
            result = json.loads(json_match.group())
            analysis.update(result)
            analysis["status"] = "completed"
        else:
            analysis["raw_analysis"] = result_text
            analysis["status"] = "partial"
            
    except Exception as e:
        analysis["status"] = "error"
        analysis["error"] = str(e)
    
    await db.paper_analyses.insert_one(analysis)
    return serialize_doc(analysis)


@router.post("/implement")
async def implement_algorithm(
    algorithm_name: str,
    algorithm_description: str,
    target_language: str = "python",
    project_id: str = None
):
    """Implement an algorithm from research"""
    
    implementation = {
        "id": str(uuid.uuid4()),
        "algorithm_name": algorithm_name,
        "target_language": target_language,
        "project_id": project_id,
        "status": "generating",
        "code": None,
        "tests": None,
        "benchmark": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Generate implementation
        code_response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": f"""Implement this algorithm in {target_language}.
Requirements:
- Production-ready code
- Proper type hints/annotations
- Documentation/comments
- Error handling
- Efficient implementation"""},
                {"role": "user", "content": f"Implement: {algorithm_name}\n\nDescription: {algorithm_description}"}
            ],
            max_tokens=4000
        )
        
        implementation["code"] = code_response.choices[0].message.content
        
        # Generate tests
        test_response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": f"Generate unit tests for this {target_language} implementation."},
                {"role": "user", "content": f"Write tests for:\n{implementation['code'][:2000]}"}
            ],
            max_tokens=2000
        )
        
        implementation["tests"] = test_response.choices[0].message.content
        implementation["status"] = "completed"
        
    except Exception as e:
        implementation["status"] = "error"
        implementation["error"] = str(e)
    
    implementation["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Store in project if specified
    if project_id and implementation["code"]:
        file_ext = {"python": ".py", "javascript": ".js", "cpp": ".cpp", "rust": ".rs"}.get(target_language, ".txt")
        
        file_record = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "filename": f"{algorithm_name.lower().replace(' ', '_')}{file_ext}",
            "filepath": f"/src/algorithms/{algorithm_name.lower().replace(' ', '_')}{file_ext}",
            "content": implementation["code"],
            "language": target_language,
            "source": "knowledge_engine",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.files.insert_one(file_record)
        implementation["file_id"] = file_record["id"]
    
    await db.algorithm_implementations.insert_one(implementation)
    return serialize_doc(implementation)


@router.get("/trending")
async def get_trending_research(category: str = "cs.AI", days: int = 7):
    """Get trending research in a category"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://export.arxiv.org/api/query",
                params={
                    "search_query": f"cat:{category}",
                    "start": 0,
                    "max_results": 20,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending"
                },
                timeout=30.0
            )
            
            papers = []
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                
                for entry in root.findall("atom:entry", ns)[:10]:
                    papers.append({
                        "title": entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else "",
                        "published": entry.find("atom:published", ns).text if entry.find("atom:published", ns) is not None else ""
                    })
            
            return {
                "category": category,
                "category_name": RESEARCH_CATEGORIES.get(category, category),
                "papers": papers,
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        return {"error": str(e)}


@router.get("/implementations")
async def list_implementations(project_id: str = None, limit: int = 20):
    """List algorithm implementations"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    return await db.algorithm_implementations.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
