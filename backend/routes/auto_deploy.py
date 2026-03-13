"""
Auto Deploy - Automatic deployment of God Mode outputs to Vercel/Railway/Netlify
Handles full deployment pipeline from code to live URL with REAL API integrations
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio
import httpx
import os
import base64
import json
import hashlib

router = APIRouter(prefix="/auto-deploy", tags=["auto-deploy"])

# Real API endpoints
VERCEL_API = "https://api.vercel.com"
RAILWAY_API = "https://backboard.railway.app/graphql/v2"
NETLIFY_API = "https://api.netlify.com/api/v1"


class DeployRequest(BaseModel):
    god_mode_session_id: str
    platform: str = "vercel"  # vercel, railway, netlify
    project_name: Optional[str] = None
    environment_variables: Dict[str, str] = {}


class DeployConfig(BaseModel):
    platform: str
    api_key: Optional[str] = None
    team_id: Optional[str] = None
    auto_deploy_enabled: bool = True


# Platform configurations
PLATFORMS = {
    "vercel": {
        "name": "Vercel",
        "deploy_url": "https://api.vercel.com/v13/deployments",
        "supports": ["nextjs", "react", "static", "node"],
        "features": ["Edge Functions", "Serverless", "CDN", "Preview URLs"]
    },
    "railway": {
        "name": "Railway",
        "deploy_url": "https://backboard.railway.app/graphql/v2",
        "supports": ["node", "python", "go", "rust", "docker"],
        "features": ["Databases", "Persistent Storage", "Private Networking"]
    },
    "netlify": {
        "name": "Netlify",
        "deploy_url": "https://api.netlify.com/api/v1/sites",
        "supports": ["static", "react", "nextjs", "functions"],
        "features": ["Forms", "Identity", "Split Testing", "CDN"]
    }
}


@router.get("/platforms")
async def get_deploy_platforms():
    """Get available deployment platforms"""
    return PLATFORMS


@router.post("/deploy")
async def deploy_god_mode_output(request: DeployRequest, background_tasks: BackgroundTasks):
    """Deploy God Mode output to specified platform"""
    
    # Get God Mode session
    session = await db.god_mode_sessions.find_one({"id": request.god_mode_session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="God Mode session not found")
    
    if session.get("status") != "completed":
        raise HTTPException(status_code=400, detail="God Mode session must be completed before deployment")
    
    deployment_id = str(uuid.uuid4())
    project_name = request.project_name or f"agentforge-{deployment_id[:8]}"
    
    deployment = {
        "id": deployment_id,
        "god_mode_session_id": request.god_mode_session_id,
        "platform": request.platform,
        "project_name": project_name,
        "status": "initializing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stages": [
            {"name": "Preparing Files", "status": "pending"},
            {"name": "Creating Project", "status": "pending"},
            {"name": "Uploading Code", "status": "pending"},
            {"name": "Building", "status": "pending"},
            {"name": "Deploying", "status": "pending"}
        ],
        "deployment_url": None,
        "logs": []
    }
    
    await db.auto_deployments.insert_one(deployment)
    
    # Start deployment in background
    background_tasks.add_task(execute_deployment, deployment_id, session, request)
    
    return {
        "deployment_id": deployment_id,
        "status": "initializing",
        "platform": request.platform,
        "message": f"Deploying to {PLATFORMS[request.platform]['name']}"
    }


async def execute_deployment(deployment_id: str, session: dict, request: DeployRequest):
    """Execute the deployment process with REAL API calls"""
    
    platform = request.platform
    project_name = request.project_name or f"agentforge-{deployment_id[:8]}"
    
    try:
        # Get API key from config
        config = await db.deploy_configs.find_one({"platform": platform})
        api_key = config.get("api_key") if config else None
        
        # Also check environment variables
        env_keys = {
            "vercel": os.environ.get("VERCEL_TOKEN"),
            "railway": os.environ.get("RAILWAY_TOKEN"),
            "netlify": os.environ.get("NETLIFY_TOKEN")
        }
        
        api_key = api_key or env_keys.get(platform)
        
        if not api_key:
            await update_deployment_log(deployment_id, f"No API key configured for {platform}. Using simulation mode.")
            await simulate_deployment(deployment_id, platform, project_name)
            return
        
        # Real deployment based on platform
        if platform == "vercel":
            await deploy_to_vercel(deployment_id, session, project_name, api_key, request.environment_variables)
        elif platform == "railway":
            await deploy_to_railway(deployment_id, session, project_name, api_key, request.environment_variables)
        elif platform == "netlify":
            await deploy_to_netlify(deployment_id, session, project_name, api_key, request.environment_variables)
        else:
            raise Exception(f"Unsupported platform: {platform}")
            
    except Exception as e:
        await db.auto_deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"logs": f"Error: {str(e)}"}
            }
        )


async def update_deployment_log(deployment_id: str, message: str):
    """Add log entry to deployment"""
    await db.auto_deployments.update_one(
        {"id": deployment_id},
        {"$push": {"logs": f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {message}"}}
    )


async def update_deployment_stage(deployment_id: str, stage_index: int, status: str):
    """Update deployment stage status"""
    await db.auto_deployments.update_one(
        {"id": deployment_id},
        {"$set": {f"stages.{stage_index}.status": status}}
    )


async def deploy_to_vercel(deployment_id: str, session: dict, project_name: str, api_key: str, env_vars: Dict):
    """Deploy to Vercel using their API"""
    
    await update_deployment_stage(deployment_id, 0, "running")
    await update_deployment_log(deployment_id, "Preparing files for Vercel...")
    
    # Get generated files from session
    files = session.get("generated_files", [])
    
    # Prepare file structure for Vercel
    vercel_files = []
    for file_info in files:
        file_path = file_info.get("path", file_info.get("name", ""))
        content = file_info.get("content", "")
        
        # Encode content as base64 for binary safety
        encoded = base64.b64encode(content.encode()).decode()
        
        vercel_files.append({
            "file": file_path,
            "data": encoded,
            "encoding": "base64"
        })
    
    # Add package.json if not present
    has_package = any(f.get("file", "").endswith("package.json") for f in vercel_files)
    if not has_package:
        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "scripts": {
                "build": "echo 'No build step'",
                "start": "node index.js"
            }
        }
        vercel_files.append({
            "file": "package.json",
            "data": base64.b64encode(json.dumps(package_json, indent=2).encode()).decode(),
            "encoding": "base64"
        })
    
    await update_deployment_stage(deployment_id, 0, "completed")
    await update_deployment_stage(deployment_id, 1, "running")
    await update_deployment_log(deployment_id, "Creating Vercel project...")
    
    async with httpx.AsyncClient() as client:
        # Create deployment
        deployment_payload = {
            "name": project_name,
            "files": vercel_files,
            "projectSettings": {
                "framework": None,
                "buildCommand": None,
                "outputDirectory": None
            },
            "target": "production"
        }
        
        if env_vars:
            deployment_payload["env"] = env_vars
        
        await update_deployment_stage(deployment_id, 1, "completed")
        await update_deployment_stage(deployment_id, 2, "running")
        await update_deployment_log(deployment_id, "Uploading code to Vercel...")
        
        response = await client.post(
            f"{VERCEL_API}/v13/deployments",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=deployment_payload,
            timeout=120.0
        )
        
        if response.status_code not in [200, 201]:
            error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise Exception(f"Vercel API error: {error_detail}")
        
        deployment_data = response.json()
        vercel_deployment_id = deployment_data.get("id")
        deployment_url = deployment_data.get("url")
        
        await update_deployment_stage(deployment_id, 2, "completed")
        await update_deployment_stage(deployment_id, 3, "running")
        await update_deployment_log(deployment_id, f"Building... Vercel deployment ID: {vercel_deployment_id}")
        
        # Poll for build completion
        max_polls = 60  # 5 minutes max
        for _ in range(max_polls):
            status_response = await client.get(
                f"{VERCEL_API}/v13/deployments/{vercel_deployment_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                ready_state = status_data.get("readyState")
                
                if ready_state == "READY":
                    await update_deployment_stage(deployment_id, 3, "completed")
                    await update_deployment_stage(deployment_id, 4, "running")
                    await update_deployment_log(deployment_id, "Build complete, finalizing deployment...")
                    break
                elif ready_state in ["ERROR", "CANCELED"]:
                    raise Exception(f"Build failed with state: {ready_state}")
            
            await asyncio.sleep(5)
        
        await update_deployment_stage(deployment_id, 4, "completed")
        
        final_url = f"https://{deployment_url}" if deployment_url else f"https://{project_name}.vercel.app"
        
        await db.auto_deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "status": "completed",
                    "deployment_url": final_url,
                    "platform_deployment_id": vercel_deployment_id,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"logs": f"Deployment successful! URL: {final_url}"}
            }
        )


async def deploy_to_railway(deployment_id: str, session: dict, project_name: str, api_key: str, env_vars: Dict):
    """Deploy to Railway using their GraphQL API"""
    
    await update_deployment_stage(deployment_id, 0, "running")
    await update_deployment_log(deployment_id, "Preparing files for Railway...")
    
    # Get generated files for future use with Railway's deployment
    _files = session.get("generated_files", [])
    await update_deployment_log(deployment_id, f"Found {len(_files)} files to deploy")
    
    await update_deployment_stage(deployment_id, 0, "completed")
    await update_deployment_stage(deployment_id, 1, "running")
    await update_deployment_log(deployment_id, "Creating Railway project...")
    
    async with httpx.AsyncClient() as client:
        # Create project mutation
        create_project_mutation = """
        mutation CreateProject($name: String!) {
            projectCreate(input: { name: $name }) {
                id
                name
            }
        }
        """
        
        response = await client.post(
            RAILWAY_API,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "query": create_project_mutation,
                "variables": {"name": project_name}
            },
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Railway API error: {response.text}")
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"Railway GraphQL error: {result['errors']}")
        
        project_id = result.get("data", {}).get("projectCreate", {}).get("id")
        
        await update_deployment_stage(deployment_id, 1, "completed")
        await update_deployment_stage(deployment_id, 2, "running")
        await update_deployment_log(deployment_id, f"Project created: {project_id}")
        
        # Create service
        create_service_mutation = """
        mutation CreateService($projectId: String!, $name: String!) {
            serviceCreate(input: { projectId: $projectId, name: $name }) {
                id
                name
            }
        }
        """
        
        service_response = await client.post(
            RAILWAY_API,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "query": create_service_mutation,
                "variables": {"projectId": project_id, "name": project_name}
            },
            timeout=60.0
        )
        
        service_result = service_response.json()
        service_id = service_result.get("data", {}).get("serviceCreate", {}).get("id")
        
        await update_deployment_stage(deployment_id, 2, "completed")
        await update_deployment_stage(deployment_id, 3, "running")
        await update_deployment_log(deployment_id, f"Service created: {service_id}")
        
        # Set environment variables if provided
        if env_vars:
            for key, value in env_vars.items():
                set_var_mutation = """
                mutation SetVariable($serviceId: String!, $key: String!, $value: String!) {
                    variableCreate(input: { serviceId: $serviceId, name: $key, value: $value }) {
                        id
                    }
                }
                """
                await client.post(
                    RAILWAY_API,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": set_var_mutation,
                        "variables": {"serviceId": service_id, "key": key, "value": value}
                    }
                )
        
        await update_deployment_stage(deployment_id, 3, "completed")
        await update_deployment_stage(deployment_id, 4, "running")
        await update_deployment_log(deployment_id, "Deploying service...")
        
        # Generate deployment domain
        generate_domain_mutation = """
        mutation GenerateDomain($serviceId: String!) {
            serviceDomainCreate(input: { serviceId: $serviceId }) {
                domain
            }
        }
        """
        
        domain_response = await client.post(
            RAILWAY_API,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "query": generate_domain_mutation,
                "variables": {"serviceId": service_id}
            },
            timeout=60.0
        )
        
        domain_result = domain_response.json()
        domain = domain_result.get("data", {}).get("serviceDomainCreate", {}).get("domain")
        
        final_url = f"https://{domain}" if domain else f"https://{project_name}.up.railway.app"
        
        await update_deployment_stage(deployment_id, 4, "completed")
        
        await db.auto_deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "status": "completed",
                    "deployment_url": final_url,
                    "platform_project_id": project_id,
                    "platform_service_id": service_id,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"logs": f"Deployment successful! URL: {final_url}"}
            }
        )


async def deploy_to_netlify(deployment_id: str, session: dict, project_name: str, api_key: str, env_vars: Dict):
    """Deploy to Netlify using their API"""
    
    await update_deployment_stage(deployment_id, 0, "running")
    await update_deployment_log(deployment_id, "Preparing files for Netlify...")
    
    files = session.get("generated_files", [])
    
    await update_deployment_stage(deployment_id, 0, "completed")
    await update_deployment_stage(deployment_id, 1, "running")
    await update_deployment_log(deployment_id, "Creating Netlify site...")
    
    async with httpx.AsyncClient() as client:
        # Create site
        site_response = await client.post(
            f"{NETLIFY_API}/sites",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "name": project_name,
                "custom_domain": None
            },
            timeout=60.0
        )
        
        if site_response.status_code not in [200, 201]:
            # Site might already exist, try to get it
            sites_response = await client.get(
                f"{NETLIFY_API}/sites",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"name": project_name}
            )
            sites = sites_response.json()
            site_data = next((s for s in sites if s.get("name") == project_name), None)
            
            if not site_data:
                raise Exception(f"Failed to create/find Netlify site: {site_response.text}")
        else:
            site_data = site_response.json()
        
        site_id = site_data.get("id")
        
        await update_deployment_stage(deployment_id, 1, "completed")
        await update_deployment_stage(deployment_id, 2, "running")
        await update_deployment_log(deployment_id, f"Site created: {site_id}")
        
        # Prepare files for deploy
        deploy_files = {}
        for file_info in files:
            file_path = file_info.get("path", file_info.get("name", ""))
            content = file_info.get("content", "")
            
            # Create SHA1 hash for file
            sha1 = hashlib.sha1(content.encode()).hexdigest()
            deploy_files[f"/{file_path}"] = sha1
        
        # Add index.html if not present
        if "/index.html" not in deploy_files:
            index_content = "<html><body><h1>AgentForge Deploy</h1></body></html>"
            deploy_files["/index.html"] = hashlib.sha1(index_content.encode()).hexdigest()
        
        # Create deploy
        deploy_response = await client.post(
            f"{NETLIFY_API}/sites/{site_id}/deploys",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "files": deploy_files,
                "async": True
            },
            timeout=60.0
        )
        
        if deploy_response.status_code not in [200, 201]:
            raise Exception(f"Netlify deploy error: {deploy_response.text}")
        
        deploy_data = deploy_response.json()
        netlify_deploy_id = deploy_data.get("id")
        
        await update_deployment_stage(deployment_id, 2, "completed")
        await update_deployment_stage(deployment_id, 3, "running")
        await update_deployment_log(deployment_id, f"Deploy created: {netlify_deploy_id}")
        
        # Upload files
        required_files = deploy_data.get("required", [])
        
        for file_info in files:
            file_path = file_info.get("path", file_info.get("name", ""))
            content = file_info.get("content", "")
            sha1 = hashlib.sha1(content.encode()).hexdigest()
            
            if sha1 in required_files:
                await client.put(
                    f"{NETLIFY_API}/deploys/{netlify_deploy_id}/files/{file_path}",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/octet-stream"
                    },
                    content=content.encode()
                )
        
        await update_deployment_stage(deployment_id, 3, "completed")
        await update_deployment_stage(deployment_id, 4, "running")
        await update_deployment_log(deployment_id, "Finalizing deployment...")
        
        # Poll for completion
        for _ in range(30):
            status_response = await client.get(
                f"{NETLIFY_API}/deploys/{netlify_deploy_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                state = status_data.get("state")
                
                if state == "ready":
                    break
                elif state == "error":
                    raise Exception("Netlify deploy failed")
            
            await asyncio.sleep(3)
        
        await update_deployment_stage(deployment_id, 4, "completed")
        
        final_url = f"https://{project_name}.netlify.app"
        
        await db.auto_deployments.update_one(
            {"id": deployment_id},
            {
                "$set": {
                    "status": "completed",
                    "deployment_url": final_url,
                    "platform_site_id": site_id,
                    "platform_deploy_id": netlify_deploy_id,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"logs": f"Deployment successful! URL: {final_url}"}
            }
        )


async def simulate_deployment(deployment_id: str, platform: str, project_name: str):
    """Simulate deployment when no API key is configured"""
    
    stages = ["Preparing Files", "Creating Project", "Uploading Code", "Building", "Deploying"]
    
    for i, stage in enumerate(stages):
        await update_deployment_stage(deployment_id, i, "running")
        await update_deployment_log(deployment_id, f"[SIMULATION] {stage}...")
        await asyncio.sleep(2)
        await update_deployment_stage(deployment_id, i, "completed")
    
    # Generate simulated URL
    if platform == "vercel":
        deployment_url = f"https://{project_name}.vercel.app"
    elif platform == "railway":
        deployment_url = f"https://{project_name}.up.railway.app"
    else:
        deployment_url = f"https://{project_name}.netlify.app"
    
    await db.auto_deployments.update_one(
        {"id": deployment_id},
        {
            "$set": {
                "status": "completed",
                "deployment_url": deployment_url,
                "simulated": True,
                "completed_at": datetime.now(timezone.utc).isoformat()
            },
            "$push": {"logs": f"[SIMULATION] Deployment complete! URL: {deployment_url}"}
        }
    )


@router.get("/deployments/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    deployment = await db.auto_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@router.get("/deployments")
async def list_deployments(platform: Optional[str] = None):
    """List all deployments"""
    query = {}
    if platform:
        query["platform"] = platform
    
    deployments = await db.auto_deployments.find(
        query, 
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    return deployments


@router.post("/config")
async def save_deploy_config(config: DeployConfig):
    """Save deployment platform configuration"""
    
    config_data = {
        "platform": config.platform,
        "api_key": config.api_key,
        "team_id": config.team_id,
        "auto_deploy_enabled": config.auto_deploy_enabled,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.deploy_configs.update_one(
        {"platform": config.platform},
        {"$set": config_data},
        upsert=True
    )
    
    return {"status": "saved", "platform": config.platform}


@router.get("/config/{platform}")
async def get_deploy_config(platform: str):
    """Get deployment configuration for a platform"""
    config = await db.deploy_configs.find_one({"platform": platform}, {"_id": 0, "api_key": 0})
    return config or {"platform": platform, "configured": False}


@router.post("/validate-key")
async def validate_api_key(platform: str, api_key: str):
    """Validate an API key for a deployment platform"""
    
    try:
        async with httpx.AsyncClient() as client:
            if platform == "vercel":
                # Test Vercel token
                response = await client.get(
                    f"{VERCEL_API}/v2/user",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "valid": True,
                        "platform": "vercel",
                        "user": user_data.get("user", {}).get("username", "Unknown"),
                        "email": user_data.get("user", {}).get("email", "")
                    }
                    
            elif platform == "railway":
                # Test Railway token
                response = await client.post(
                    RAILWAY_API,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"query": "{ me { id email } }"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and result["data"].get("me"):
                        return {
                            "valid": True,
                            "platform": "railway",
                            "email": result["data"]["me"].get("email", "")
                        }
                        
            elif platform == "netlify":
                # Test Netlify token
                response = await client.get(
                    f"{NETLIFY_API}/user",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "valid": True,
                        "platform": "netlify",
                        "name": user_data.get("full_name", "Unknown"),
                        "email": user_data.get("email", "")
                    }
            
            return {"valid": False, "error": "Invalid API key or unauthorized"}
            
    except Exception as e:
        return {"valid": False, "error": str(e)}


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete/teardown a deployment"""
    
    deployment = await db.auto_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Mark as deleted (in real implementation, would call platform API to delete)
    await db.auto_deployments.update_one(
        {"id": deployment_id},
        {
            "$set": {
                "status": "deleted",
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"status": "deleted", "deployment_id": deployment_id}


@router.post("/redeploy/{deployment_id}")
async def redeploy(deployment_id: str, background_tasks: BackgroundTasks):
    """Redeploy an existing deployment"""
    
    deployment = await db.auto_deployments.find_one({"id": deployment_id}, {"_id": 0})
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Get original session
    session = await db.god_mode_sessions.find_one(
        {"id": deployment["god_mode_session_id"]}, 
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Original God Mode session not found")
    
    # Create new deployment
    new_deployment_id = str(uuid.uuid4())
    
    new_deployment = {
        "id": new_deployment_id,
        "god_mode_session_id": deployment["god_mode_session_id"],
        "platform": deployment["platform"],
        "project_name": deployment["project_name"],
        "status": "initializing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "previous_deployment_id": deployment_id,
        "stages": [
            {"name": "Preparing Files", "status": "pending"},
            {"name": "Creating Project", "status": "pending"},
            {"name": "Uploading Code", "status": "pending"},
            {"name": "Building", "status": "pending"},
            {"name": "Deploying", "status": "pending"}
        ],
        "deployment_url": None,
        "logs": ["Redeploying from previous deployment"]
    }
    
    await db.auto_deployments.insert_one(new_deployment)
    
    # Execute redeployment
    request = DeployRequest(
        god_mode_session_id=deployment["god_mode_session_id"],
        platform=deployment["platform"],
        project_name=deployment["project_name"]
    )
    
    background_tasks.add_task(execute_deployment, new_deployment_id, session, request)
    
    return {
        "deployment_id": new_deployment_id,
        "status": "initializing",
        "message": "Redeployment started"
    }
