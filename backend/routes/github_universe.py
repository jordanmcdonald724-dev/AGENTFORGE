"""
GitHub Universe Control
=======================
AI maintainer for software everywhere.
Scan repos, learn patterns, auto-fix bugs, propose pull requests.
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

router = APIRouter(prefix="/github-universe", tags=["github-universe"])

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


@router.get("/status")
async def get_github_status():
    """Get GitHub integration status"""
    return {
        "connected": bool(GITHUB_TOKEN),
        "features": [
            "repo_scanning",
            "pattern_learning", 
            "auto_fix",
            "pull_requests",
            "vulnerability_detection"
        ]
    }


@router.post("/scan")
async def scan_repository(repo_url: str, deep_scan: bool = False):
    """Scan a GitHub repository for patterns, issues, and improvements"""
    
    # Parse repo URL
    parts = repo_url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid repo URL")
    
    owner, repo = parts[0], parts[1].replace(".git", "")
    
    scan_result = {
        "id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "owner": owner,
        "repo": repo,
        "status": "scanning",
        "findings": [],
        "patterns_detected": [],
        "vulnerabilities": [],
        "improvements": [],
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    try:
        async with httpx.AsyncClient() as client:
            # Get repo info
            repo_res = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers,
                timeout=30.0
            )
            
            if repo_res.status_code == 200:
                repo_data = repo_res.json()
                scan_result["repo_info"] = {
                    "name": repo_data.get("name"),
                    "description": repo_data.get("description"),
                    "language": repo_data.get("language"),
                    "stars": repo_data.get("stargazers_count"),
                    "forks": repo_data.get("forks_count"),
                    "open_issues": repo_data.get("open_issues_count")
                }
            
            # Get file tree
            tree_res = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers=headers,
                timeout=30.0
            )
            
            if tree_res.status_code == 200:
                tree_data = tree_res.json()
                files = [f["path"] for f in tree_data.get("tree", []) if f["type"] == "blob"]
                scan_result["file_count"] = len(files)
                scan_result["file_types"] = _analyze_file_types(files)
                
                # Detect patterns based on files
                scan_result["patterns_detected"] = _detect_patterns(files)
            
            # Get recent commits for activity analysis
            commits_res = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=10",
                headers=headers,
                timeout=30.0
            )
            
            if commits_res.status_code == 200:
                commits = commits_res.json()
                scan_result["recent_activity"] = {
                    "last_commit": commits[0]["commit"]["committer"]["date"] if commits else None,
                    "commit_frequency": len(commits)
                }
        
        scan_result["status"] = "completed"
        
    except Exception as e:
        scan_result["status"] = "error"
        scan_result["error"] = str(e)
    
    scan_result["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Store scan result
    await db.github_scans.insert_one(scan_result)
    
    return serialize_doc(scan_result)


def _analyze_file_types(files: List[str]) -> Dict[str, int]:
    """Analyze file types in repository"""
    types = {}
    for f in files:
        ext = f.split(".")[-1] if "." in f else "other"
        types[ext] = types.get(ext, 0) + 1
    return dict(sorted(types.items(), key=lambda x: -x[1])[:10])


def _detect_patterns(files: List[str]) -> List[Dict[str, Any]]:
    """Detect architectural patterns from file structure"""
    patterns = []
    file_str = " ".join(files).lower()
    
    if "package.json" in file_str:
        patterns.append({"pattern": "node_project", "confidence": 0.95})
    if "requirements.txt" in file_str or "setup.py" in file_str:
        patterns.append({"pattern": "python_project", "confidence": 0.95})
    if "src/components" in file_str or "src/pages" in file_str:
        patterns.append({"pattern": "react_app", "confidence": 0.9})
    if "docker" in file_str:
        patterns.append({"pattern": "containerized", "confidence": 0.9})
    if "test" in file_str or "spec" in file_str:
        patterns.append({"pattern": "has_tests", "confidence": 0.85})
    if ".github/workflows" in file_str:
        patterns.append({"pattern": "ci_cd", "confidence": 0.95})
    if "api" in file_str or "routes" in file_str:
        patterns.append({"pattern": "has_api", "confidence": 0.8})
    
    return patterns


@router.post("/analyze-code")
async def analyze_code_quality(repo_url: str, file_path: str = None):
    """Analyze code quality and suggest improvements"""
    
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner, repo = parts[0], parts[1].replace(".git", "")
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    analysis = {
        "id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "issues": [],
        "improvements": [],
        "auto_fixes": []
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Get a sample file to analyze
            if file_path:
                content_res = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}",
                    headers=headers,
                    timeout=30.0
                )
                
                if content_res.status_code == 200:
                    import base64
                    content_data = content_res.json()
                    code = base64.b64decode(content_data.get("content", "")).decode("utf-8")
                    
                    # Use LLM to analyze code
                    llm_response = llm_client.chat.completions.create(
                        model="google/gemini-2.5-flash",
                        messages=[
                            {"role": "system", "content": """You are a code analyzer. Analyze the code and output JSON:
{
    "issues": [{"type": "bug|performance|security|style", "description": "...", "line": N, "severity": "high|medium|low"}],
    "improvements": [{"description": "...", "benefit": "..."}],
    "auto_fixes": [{"issue": "...", "fix": "code snippet"}]
}"""},
                            {"role": "user", "content": f"Analyze this code:\n\n{code[:5000]}"}
                        ],
                        max_tokens=3000
                    )
                    
                    import json
                    import re
                    result_text = llm_response.choices[0].message.content
                    json_match = re.search(r'\{[\s\S]*\}', result_text)
                    if json_match:
                        result = json.loads(json_match.group())
                        analysis["issues"] = result.get("issues", [])
                        analysis["improvements"] = result.get("improvements", [])
                        analysis["auto_fixes"] = result.get("auto_fixes", [])
    
    except Exception as e:
        analysis["error"] = str(e)
    
    analysis["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    await db.code_analyses.insert_one(analysis)
    
    return serialize_doc(analysis)


@router.post("/auto-fix")
async def generate_auto_fix(repo_url: str, issue_description: str):
    """Generate automatic fix for an issue"""
    
    fix_result = {
        "id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "issue": issue_description,
        "status": "generating"
    }
    
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """You are an expert code fixer. Generate a fix for the described issue.
Output JSON:
{
    "fix_description": "What the fix does",
    "files_to_modify": ["file1.py", "file2.js"],
    "code_changes": [{"file": "...", "before": "...", "after": "..."}],
    "pr_title": "Fix: ...",
    "pr_body": "Description of changes..."
}"""},
                {"role": "user", "content": f"Generate fix for: {issue_description}"}
            ],
            max_tokens=4000
        )
        
        import json
        import re
        result_text = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            fix_data = json.loads(json_match.group())
            fix_result.update(fix_data)
            fix_result["status"] = "ready"
        else:
            fix_result["raw_response"] = result_text
            fix_result["status"] = "generated"
            
    except Exception as e:
        fix_result["status"] = "error"
        fix_result["error"] = str(e)
    
    fix_result["generated_at"] = datetime.now(timezone.utc).isoformat()
    await db.auto_fixes.insert_one(fix_result)
    
    return serialize_doc(fix_result)


@router.post("/create-pr")
async def create_pull_request(
    repo_url: str,
    title: str,
    body: str,
    branch: str = "agentforge-fix",
    base: str = "main",
    changes: List[dict] = None
):
    """Create a pull request with proposed changes"""
    
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=400, detail="GitHub token required")
    
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner, repo = parts[0], parts[1].replace(".git", "")
    
    pr_result = {
        "id": str(uuid.uuid4()),
        "repo_url": repo_url,
        "title": title,
        "status": "pending",
        "pr_url": None
    }
    
    # Note: Actually creating PRs requires more complex Git operations
    # This creates a record of the proposed PR
    pr_result["proposed_changes"] = changes or []
    pr_result["branch"] = branch
    pr_result["base"] = base
    pr_result["body"] = body
    pr_result["status"] = "proposed"
    pr_result["created_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.proposed_prs.insert_one(pr_result)
    
    return serialize_doc(pr_result)


@router.get("/scans")
async def list_scans(limit: int = 20):
    """List recent repository scans"""
    return await db.github_scans.find({}, {"_id": 0}).sort("started_at", -1).to_list(limit)


@router.get("/learn-patterns")
async def learn_patterns_from_repos(language: str = "javascript", count: int = 10):
    """Learn patterns from top repositories"""
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    learned = {
        "language": language,
        "repos_analyzed": 0,
        "patterns": [],
        "best_practices": []
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Search for top repos
            search_res = await client.get(
                f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&per_page={count}",
                headers=headers,
                timeout=30.0
            )
            
            if search_res.status_code == 200:
                repos = search_res.json().get("items", [])
                learned["repos_analyzed"] = len(repos)
                
                # Extract common patterns
                for repo in repos:
                    learned["patterns"].append({
                        "repo": repo["full_name"],
                        "stars": repo["stargazers_count"],
                        "topics": repo.get("topics", [])[:5]
                    })
        
        # Use LLM to synthesize best practices
        if learned["patterns"]:
            response = llm_client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": f"Based on top {language} repositories, list 5 best practices."},
                    {"role": "user", "content": f"Repos analyzed: {[p['repo'] for p in learned['patterns']]}"}
                ],
                max_tokens=1000
            )
            learned["best_practices"] = response.choices[0].message.content.split("\n")[:5]
            
    except Exception as e:
        learned["error"] = str(e)
    
    learned["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    return learned
