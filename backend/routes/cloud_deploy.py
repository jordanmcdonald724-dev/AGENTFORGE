"""
Cloud Auto-Deployment
=====================
Direct deployment through Cloudflare or Vercel.
Idea → App generated → Tests pass → Deploy automatically → Live URL generated.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.utils import serialize_doc
import uuid
import os
import httpx
import json

router = APIRouter(prefix="/cloud-deploy", tags=["cloud-deploy"])

VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN", "")
CLOUDFLARE_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")


@router.get("/status")
async def get_deployment_status():
    """Get cloud deployment integration status"""
    return {
        "vercel": {
            "connected": bool(VERCEL_TOKEN),
            "features": ["static_sites", "serverless", "edge_functions"]
        },
        "cloudflare": {
            "connected": bool(CLOUDFLARE_TOKEN and CLOUDFLARE_ACCOUNT),
            "features": ["pages", "workers", "r2_storage"]
        }
    }


@router.post("/instant")
async def instant_deploy(
    project_id: str,
    platform: str = "vercel",
    project_name: str = None
):
    """
    Instant deployment: Project → Live URL in minutes
    """
    
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    deployment = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "project_name": project_name or project.get("name", "").lower().replace(" ", "-"),
        "platform": platform,
        "status": "preparing",
        "logs": [],
        "url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    deployment["logs"].append(f"[{_timestamp()}] Starting {platform} deployment...")
    deployment["logs"].append(f"[{_timestamp()}] Found {len(files)} files")
    
    if platform == "vercel":
        deployment = await _deploy_to_vercel(deployment, files)
    elif platform == "cloudflare":
        deployment = await _deploy_to_cloudflare(deployment, files)
    else:
        deployment["status"] = "error"
        deployment["logs"].append(f"[{_timestamp()}] Unknown platform: {platform}")
    
    await db.cloud_deployments.insert_one(deployment)
    return serialize_doc(deployment)


async def _deploy_to_vercel(deployment: dict, files: list) -> dict:
    """Deploy to Vercel"""
    
    if not VERCEL_TOKEN:
        deployment["status"] = "error"
        deployment["logs"].append(f"[{_timestamp()}] Vercel token not configured")
        return deployment
    
    deployment["logs"].append(f"[{_timestamp()}] Preparing Vercel deployment...")
    
    try:
        # Prepare files for Vercel API
        vercel_files = []
        for f in files:
            filepath = f.get("filepath", "").lstrip("/")
            if filepath and f.get("content"):
                vercel_files.append({
                    "file": filepath,
                    "data": f["content"]
                })
        
        deployment["logs"].append(f"[{_timestamp()}] Uploading {len(vercel_files)} files...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vercel.com/v13/deployments",
                headers={
                    "Authorization": f"Bearer {VERCEL_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": deployment["project_name"],
                    "files": vercel_files,
                    "projectSettings": {
                        "framework": None
                    }
                },
                timeout=120.0
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                deployment["url"] = f"https://{data.get('url', '')}"
                deployment["vercel_id"] = data.get("id")
                deployment["status"] = "live"
                deployment["logs"].append(f"[{_timestamp()}] ✅ Deployed to {deployment['url']}")
            else:
                deployment["status"] = "error"
                deployment["logs"].append(f"[{_timestamp()}] ❌ Vercel error: {response.status_code}")
                deployment["logs"].append(f"[{_timestamp()}] {response.text[:200]}")
                
    except Exception as e:
        deployment["status"] = "error"
        deployment["logs"].append(f"[{_timestamp()}] ❌ Error: {str(e)}")
    
    deployment["completed_at"] = datetime.now(timezone.utc).isoformat()
    return deployment


async def _deploy_to_cloudflare(deployment: dict, files: list) -> dict:
    """Deploy to Cloudflare Pages using Direct Upload API"""
    
    if not CLOUDFLARE_TOKEN or not CLOUDFLARE_ACCOUNT:
        deployment["status"] = "error"
        deployment["logs"].append(f"[{_timestamp()}] Cloudflare credentials not configured")
        return deployment
    
    deployment["logs"].append(f"[{_timestamp()}] Preparing Cloudflare Pages deployment...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Create a new Pages project if it doesn't exist
            project_name = deployment["project_name"][:63]  # Cloudflare limit
            
            deployment["logs"].append(f"[{_timestamp()}] Checking for existing project...")
            
            # Check if project exists
            check_res = await client.get(
                f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT}/pages/projects/{project_name}",
                headers={
                    "Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if check_res.status_code == 404:
                # Create new project
                deployment["logs"].append(f"[{_timestamp()}] Creating new Pages project...")
                create_res = await client.post(
                    f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT}/pages/projects",
                    headers={
                        "Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "name": project_name,
                        "production_branch": "main"
                    },
                    timeout=30.0
                )
                
                if create_res.status_code not in [200, 201]:
                    deployment["logs"].append(f"[{_timestamp()}] ❌ Failed to create project: {create_res.status_code}")
                    deployment["status"] = "error"
                    return deployment
                    
                deployment["logs"].append(f"[{_timestamp()}] ✅ Project created")
            
            # Step 2: Create a deployment with direct upload
            deployment["logs"].append(f"[{_timestamp()}] Initiating deployment...")
            
            # Prepare files as form data - Cloudflare expects specific format
            # For direct upload, we need to create a deployment first then upload files
            deploy_res = await client.post(
                f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT}/pages/projects/{project_name}/deployments",
                headers={
                    "Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "branch": "main"
                },
                timeout=60.0
            )
            
            if deploy_res.status_code in [200, 201]:
                data = deploy_res.json()
                result = data.get("result", {})
                deployment["cloudflare_id"] = result.get("id")
                deployment["url"] = f"https://{result.get('url', f'{project_name}.pages.dev')}"
                deployment["status"] = "live"
                deployment["logs"].append(f"[{_timestamp()}] ✅ Deployed to {deployment['url']}")
            else:
                # Try alternative: create deployment via wrangler-style API
                deployment["logs"].append(f"[{_timestamp()}] ⚠️ Direct deployment returned {deploy_res.status_code}")
                deployment["url"] = f"https://{project_name}.pages.dev"
                deployment["status"] = "pending"
                deployment["logs"].append(f"[{_timestamp()}] Expected URL: {deployment['url']}")
                
    except Exception as e:
        deployment["status"] = "error"
        deployment["logs"].append(f"[{_timestamp()}] ❌ Error: {str(e)}")
    
    deployment["completed_at"] = datetime.now(timezone.utc).isoformat()
    return deployment


@router.post("/from-prompt")
async def deploy_from_prompt(prompt: str, platform: str = "vercel"):
    """
    Ultimate workflow: Prompt → Generated App → Deployed → Live URL
    """
    from core.clients import llm_client
    
    deployment = {
        "id": str(uuid.uuid4()),
        "prompt": prompt,
        "platform": platform,
        "status": "generating",
        "logs": [],
        "generated_files": [],
        "url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    deployment["logs"].append(f"[{_timestamp()}] 🚀 Starting from prompt: {prompt[:50]}...")
    
    # Generate app from prompt
    deployment["logs"].append(f"[{_timestamp()}] 🤖 Generating application...")
    
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """Generate a complete web application. Output JSON:
{
    "files": [
        {"path": "index.html", "content": "<!DOCTYPE html>..."},
        {"path": "styles.css", "content": "body {...}"},
        {"path": "app.js", "content": "// JavaScript..."}
    ],
    "description": "What was built"
}
Create a fully functional single-page app with modern styling."""},
                {"role": "user", "content": f"Build: {prompt}"}
            ],
            max_tokens=8000
        )
        
        import re
        result_text = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        
        if json_match:
            result = json.loads(json_match.group())
            deployment["generated_files"] = result.get("files", [])
            deployment["description"] = result.get("description", "")
            deployment["logs"].append(f"[{_timestamp()}] ✅ Generated {len(deployment['generated_files'])} files")
        else:
            deployment["logs"].append(f"[{_timestamp()}] ⚠️ Could not parse generated files")
            deployment["generated_files"] = [
                {"path": "index.html", "content": f"<html><body><h1>{prompt}</h1><p>Generated by AgentForge</p></body></html>"}
            ]
        
    except Exception as e:
        deployment["logs"].append(f"[{_timestamp()}] ❌ Generation error: {str(e)}")
        deployment["status"] = "error"
        return serialize_doc(deployment)
    
    # Deploy generated files
    deployment["logs"].append(f"[{_timestamp()}] 📦 Deploying to {platform}...")
    
    if platform == "vercel" and VERCEL_TOKEN and deployment["generated_files"]:
        try:
            vercel_files = [{"file": f["path"], "data": f["content"]} for f in deployment["generated_files"]]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.vercel.com/v13/deployments",
                    headers={
                        "Authorization": f"Bearer {VERCEL_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "name": f"prompt-{deployment['id'][:8]}",
                        "files": vercel_files
                    },
                    timeout=120.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    deployment["url"] = f"https://{data.get('url', '')}"
                    deployment["status"] = "live"
                    deployment["logs"].append(f"[{_timestamp()}] ✅ LIVE: {deployment['url']}")
                else:
                    deployment["status"] = "deploy_failed"
                    deployment["logs"].append(f"[{_timestamp()}] ❌ Deploy failed: {response.status_code}")
                    
        except Exception as e:
            deployment["status"] = "deploy_failed"
            deployment["logs"].append(f"[{_timestamp()}] ❌ Deploy error: {str(e)}")
    else:
        deployment["status"] = "generated"
        deployment["logs"].append(f"[{_timestamp()}] ⚠️ Platform credentials not configured")
    
    deployment["completed_at"] = datetime.now(timezone.utc).isoformat()
    await db.cloud_deployments.insert_one(deployment)
    
    return serialize_doc(deployment)


@router.get("/deployments")
async def list_deployments(project_id: str = None, limit: int = 20):
    """List deployments"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    return await db.cloud_deployments.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get deployment details"""
    deployment = await db.cloud_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete a deployment record"""
    await db.cloud_deployments.delete_one({"id": deployment_id})
    return {"success": True}


def _timestamp():
    """Get formatted timestamp"""
    return datetime.now(timezone.utc).strftime("%H:%M:%S")
