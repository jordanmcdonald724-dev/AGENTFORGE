"""
Global Codebase Intelligence
============================
Integration with the GitHub ecosystem.
Analyze thousands of repositories → Learn best architectures → Detect vulnerabilities → Generate improvements.
Your system becomes a global software intelligence engine.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import os
import httpx

router = APIRouter(prefix="/global-intelligence", tags=["global-intelligence"])

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


@router.get("/status")
async def get_intelligence_status():
    """Get global intelligence system status"""
    
    analyses = await db.global_analyses.count_documents({})
    patterns = await db.global_patterns.count_documents({})
    
    return {
        "active": True,
        "repos_analyzed": analyses,
        "patterns_learned": patterns,
        "capabilities": [
            "architecture_analysis",
            "vulnerability_detection",
            "best_practice_extraction",
            "code_pattern_learning",
            "improvement_generation"
        ]
    }


@router.post("/analyze-ecosystem")
async def analyze_ecosystem(
    language: str = "javascript",
    topic: str = None,
    min_stars: int = 1000,
    limit: int = 10
):
    """Analyze top repositories in an ecosystem"""
    
    analysis = {
        "id": str(uuid.uuid4()),
        "language": language,
        "topic": topic,
        "min_stars": min_stars,
        "status": "analyzing",
        "repos_analyzed": [],
        "patterns_found": [],
        "best_practices": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    try:
        async with httpx.AsyncClient() as client:
            # Search for top repos
            query = f"language:{language}"
            if topic:
                query += f" topic:{topic}"
            query += f" stars:>={min_stars}"
            
            response = await client.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": limit
                },
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                repos = response.json().get("items", [])
                
                for repo in repos:
                    repo_info = {
                        "name": repo["full_name"],
                        "stars": repo["stargazers_count"],
                        "description": repo.get("description", "")[:200],
                        "topics": repo.get("topics", [])[:5],
                        "language": repo["language"]
                    }
                    analysis["repos_analyzed"].append(repo_info)
        
        # Use LLM to extract patterns
        if analysis["repos_analyzed"]:
            llm_response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": """Analyze these top repositories and extract:
1. Common architectural patterns
2. Best practices
3. Technology choices
4. Code organization patterns

Output JSON:
{
    "patterns": [{"name": "...", "description": "...", "frequency": "high|medium|low"}],
    "best_practices": [{"practice": "...", "rationale": "..."}],
    "tech_trends": ["trend1", "trend2"],
    "recommendations": ["rec1", "rec2"]
}"""},
                    {"role": "user", "content": f"Analyze {language} ecosystem:\n{analysis['repos_analyzed']}"}
                ],
                max_tokens=2000
            )
            
            import json
            import re
            result_text = llm_response.choices[0].message.content
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            
            if json_match:
                result = json.loads(json_match.group())
                analysis["patterns_found"] = result.get("patterns", [])
                analysis["best_practices"] = result.get("best_practices", [])
                analysis["tech_trends"] = result.get("tech_trends", [])
                analysis["recommendations"] = result.get("recommendations", [])
        
        analysis["status"] = "completed"
        
    except Exception as e:
        analysis["status"] = "error"
        analysis["error"] = str(e)
    
    analysis["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Store patterns for learning
    for pattern in analysis.get("patterns_found", []):
        await db.global_patterns.update_one(
            {"name": pattern["name"], "language": language},
            {"$set": pattern, "$inc": {"occurrences": 1}},
            upsert=True
        )
    
    await db.global_analyses.insert_one(analysis)
    return serialize_doc(analysis)


@router.post("/detect-vulnerabilities")
async def detect_vulnerabilities(repo_url: str):
    """Detect potential vulnerabilities in a repository"""
    
    parts = repo_url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid repo URL")
    
    owner, repo = parts[0], parts[1].replace(".git", "")
    
    detection = {
        "id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "status": "scanning",
        "vulnerabilities": [],
        "security_score": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    try:
        async with httpx.AsyncClient() as client:
            # Get repo contents for analysis
            tree_response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers=headers,
                timeout=30.0
            )
            
            files = []
            if tree_response.status_code == 200:
                tree = tree_response.json().get("tree", [])
                files = [f["path"] for f in tree if f["type"] == "blob"]
        
        # Analyze for vulnerabilities
        file_list = files[:50]  # Limit for analysis
        
        llm_response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """Analyze this repository structure for security vulnerabilities.
Look for:
- Hardcoded credentials
- Insecure dependencies
- Missing security headers
- SQL injection risks
- XSS vulnerabilities
- Insecure configurations

Output JSON:
{
    "vulnerabilities": [{"type": "...", "severity": "critical|high|medium|low", "description": "...", "file": "...", "recommendation": "..."}],
    "security_score": 0-100,
    "security_summary": "Overall assessment"
}"""},
                {"role": "user", "content": f"Analyze security of {repo_url}:\nFiles: {file_list}"}
            ],
            max_tokens=2000
        )
        
        import json
        import re
        result_text = llm_response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        
        if json_match:
            result = json.loads(json_match.group())
            detection["vulnerabilities"] = result.get("vulnerabilities", [])
            detection["security_score"] = result.get("security_score", 50)
            detection["security_summary"] = result.get("security_summary", "")
        
        detection["status"] = "completed"
        
    except Exception as e:
        detection["status"] = "error"
        detection["error"] = str(e)
    
    detection["completed_at"] = datetime.now(timezone.utc).isoformat()
    await db.vulnerability_scans.insert_one(detection)
    
    return serialize_doc(detection)


@router.post("/learn-architecture")
async def learn_architecture(repo_url: str, project_id: str = None):
    """Learn architecture patterns from a repository and apply to project"""
    
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner, repo = parts[0], parts[1].replace(".git", "")
    
    learning = {
        "id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "project_id": project_id,
        "status": "learning",
        "architecture": {},
        "applicable_patterns": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    try:
        async with httpx.AsyncClient() as client:
            # Get file structure
            tree_response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers=headers,
                timeout=30.0
            )
            
            if tree_response.status_code == 200:
                tree = tree_response.json().get("tree", [])
                files = [f["path"] for f in tree if f["type"] == "blob"]
                dirs = [f["path"] for f in tree if f["type"] == "tree"]
                
                learning["file_count"] = len(files)
                learning["directory_structure"] = dirs[:20]
        
        # Analyze architecture
        llm_response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """Analyze the repository architecture and extract patterns.
Output JSON:
{
    "architecture_type": "monolith|microservices|modular|etc",
    "patterns": [{"name": "...", "description": "...", "implementation": "..."}],
    "folder_structure": {"description": "...", "benefits": ["..."]},
    "tech_stack": ["tech1", "tech2"],
    "applicable_to_projects": ["project_type1", "project_type2"],
    "adoption_guide": "How to adopt this architecture"
}"""},
                {"role": "user", "content": f"Learn architecture from {repo_url}:\nDirs: {learning.get('directory_structure', [])}"}
            ],
            max_tokens=2000
        )
        
        import json
        import re
        result_text = llm_response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        
        if json_match:
            result = json.loads(json_match.group())
            learning["architecture"] = result
            learning["applicable_patterns"] = result.get("patterns", [])
        
        learning["status"] = "completed"
        
    except Exception as e:
        learning["status"] = "error"
        learning["error"] = str(e)
    
    learning["completed_at"] = datetime.now(timezone.utc).isoformat()
    await db.architecture_learnings.insert_one(learning)
    
    return serialize_doc(learning)


@router.get("/patterns")
async def get_learned_patterns(language: str = None, limit: int = 50):
    """Get all learned patterns"""
    query = {}
    if language:
        query["language"] = language
    return await db.global_patterns.find(query, {"_id": 0}).sort("occurrences", -1).to_list(limit)


@router.get("/analyses")
async def list_analyses(language: str = None, limit: int = 20):
    """List ecosystem analyses"""
    query = {}
    if language:
        query["language"] = language
    return await db.global_analyses.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.post("/generate-improvements")
async def generate_improvements(project_id: str):
    """Generate improvements for a project based on global intelligence"""
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(50)
    patterns = await db.global_patterns.find({}).sort("occurrences", -1).to_list(20)
    
    improvements = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "status": "generating",
        "suggestions": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        file_summary = [f.get("filepath", "") for f in files][:20]
        pattern_summary = [p.get("name", "") for p in patterns][:10]
        
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """Based on global intelligence patterns, suggest improvements.
Output JSON:
{
    "suggestions": [
        {
            "type": "architecture|code|performance|security",
            "priority": "high|medium|low",
            "title": "...",
            "description": "...",
            "implementation": "How to implement",
            "based_on_pattern": "Pattern name this is based on"
        }
    ],
    "overall_assessment": "Project quality assessment",
    "top_priority": "Most important improvement"
}"""},
                {"role": "user", "content": f"""Project: {project.get('name')}
Files: {file_summary}
Known good patterns: {pattern_summary}
Generate improvements."""}
            ],
            max_tokens=3000
        )
        
        import json
        import re
        result_text = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        
        if json_match:
            result = json.loads(json_match.group())
            improvements["suggestions"] = result.get("suggestions", [])
            improvements["overall_assessment"] = result.get("overall_assessment", "")
            improvements["top_priority"] = result.get("top_priority", "")
        
        improvements["status"] = "completed"
        
    except Exception as e:
        improvements["status"] = "error"
        improvements["error"] = str(e)
    
    improvements["completed_at"] = datetime.now(timezone.utc).isoformat()
    await db.improvement_suggestions.insert_one(improvements)
    
    return serialize_doc(improvements)
