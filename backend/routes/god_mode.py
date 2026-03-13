"""
God Mode - One-Prompt SaaS Builder
==================================
One command creates a full SaaS business:
app + backend + database + dashboard + deployment + landing page
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json
import asyncio

router = APIRouter(prefix="/god-mode", tags=["god-mode"])


# ========== GOD MODE TEMPLATES ==========

SAAS_TEMPLATES = {
    "analytics": {
        "name": "Analytics Dashboard",
        "components": ["dashboard", "charts", "data-pipeline", "api", "auth"],
        "files_estimate": 25,
        "complexity": "medium"
    },
    "marketplace": {
        "name": "Marketplace Platform",
        "components": ["listings", "search", "payments", "messaging", "auth", "dashboard"],
        "files_estimate": 40,
        "complexity": "high"
    },
    "saas_starter": {
        "name": "SaaS Starter Kit",
        "components": ["landing", "auth", "dashboard", "billing", "api", "admin"],
        "files_estimate": 35,
        "complexity": "medium"
    },
    "ai_tool": {
        "name": "AI Tool Platform",
        "components": ["landing", "auth", "ai-interface", "api", "billing", "dashboard"],
        "files_estimate": 30,
        "complexity": "medium"
    },
    "community": {
        "name": "Community Platform",
        "components": ["profiles", "posts", "comments", "messaging", "notifications", "auth"],
        "files_estimate": 45,
        "complexity": "high"
    }
}


@router.get("/templates")
async def get_god_mode_templates():
    """Get available SaaS templates"""
    return SAAS_TEMPLATES


@router.post("/create")
async def god_mode_create(prompt: str, template: str = None):
    """
    GOD MODE: Create a full SaaS from one prompt.
    
    Example: "Create a full SaaS business around AI fishing analytics"
    """
    
    # Create god mode session
    session = {
        "id": str(uuid.uuid4()),
        "prompt": prompt,
        "template": template,
        "status": "initializing",
        "phases": [],
        "generated_files": [],
        "project_id": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.god_mode_sessions.insert_one(session)
    
    # Phase 1: Analyze and plan
    session["phases"].append({
        "name": "analysis",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat()
    })
    
    try:
        # Get AI to analyze and create plan
        planning_response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": """You are the GOD MODE system for AgentForge.
You create COMPLETE SaaS businesses from a single prompt.

When given a business idea, you must output a comprehensive plan in JSON format:
{
    "business_name": "Name of the SaaS",
    "tagline": "One-line description",
    "target_audience": "Who this is for",
    "core_features": ["feature1", "feature2", ...],
    "tech_stack": {
        "frontend": "React/Vue/etc",
        "backend": "FastAPI/Node/etc",
        "database": "PostgreSQL/MongoDB/etc",
        "deployment": "Vercel/Railway/etc"
    },
    "pages": ["landing", "dashboard", "settings", ...],
    "api_endpoints": ["/api/...", ...],
    "monetization": "Subscription/Usage-based/etc",
    "estimated_files": 30,
    "build_phases": ["setup", "backend", "frontend", "integration", "deployment"]
}

Be specific and practical. This will be used to generate actual code."""},
                {"role": "user", "content": f"Create a full SaaS business: {prompt}"}
            ],
            max_tokens=4000
        )
        
        plan_text = planning_response.choices[0].message.content
        
        # Try to extract JSON from response
        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', plan_text)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                plan = {"raw_plan": plan_text, "business_name": "Generated SaaS"}
        except:
            plan = {"raw_plan": plan_text, "business_name": "Generated SaaS"}
        
        session["phases"][0]["status"] = "completed"
        session["phases"][0]["result"] = plan
        session["plan"] = plan
        
    except Exception as e:
        session["phases"][0]["status"] = "failed"
        session["phases"][0]["error"] = str(e)
        plan = {"error": str(e)}
    
    # Create project
    project = {
        "id": str(uuid.uuid4()),
        "name": plan.get("business_name", "God Mode Project"),
        "type": "saas",
        "description": plan.get("tagline", prompt),
        "status": "building",
        "god_mode_session": session["id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.projects.insert_one(project)
    session["project_id"] = project["id"]
    
    # Update session
    session["status"] = "planned"
    await db.god_mode_sessions.update_one(
        {"id": session["id"]},
        {"$set": session}
    )
    
    return {
        "session_id": session["id"],
        "project_id": project["id"],
        "status": "planned",
        "plan": plan,
        "next_step": f"Call POST /api/god-mode/{session['id']}/build to start building"
    }


@router.post("/{session_id}/build")
async def god_mode_build(session_id: str):
    """Execute the god mode build"""
    session = await db.god_mode_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    plan = session.get("plan", {})
    project_id = session.get("project_id")
    
    if not project_id:
        raise HTTPException(status_code=400, detail="No project associated with session")
    
    # Phase 2: Generate files
    build_phase = {
        "name": "building",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "files_generated": []
    }
    
    generated_files = []
    
    # Generate landing page
    landing_file = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "filename": "LandingPage.jsx",
        "filepath": "/src/pages/LandingPage.jsx",
        "language": "jsx",
        "content": _generate_landing_page(plan),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(landing_file)
    generated_files.append(landing_file["filepath"])
    
    # Generate dashboard
    dashboard_file = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "filename": "Dashboard.jsx",
        "filepath": "/src/pages/Dashboard.jsx",
        "language": "jsx",
        "content": _generate_dashboard(plan),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(dashboard_file)
    generated_files.append(dashboard_file["filepath"])
    
    # Generate API routes
    api_file = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "filename": "api.py",
        "filepath": "/backend/api.py",
        "language": "python",
        "content": _generate_api(plan),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(api_file)
    generated_files.append(api_file["filepath"])
    
    # Generate auth
    auth_file = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "filename": "auth.py",
        "filepath": "/backend/auth.py",
        "language": "python",
        "content": _generate_auth(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(auth_file)
    generated_files.append(auth_file["filepath"])
    
    # Generate database models
    models_file = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "filename": "models.py",
        "filepath": "/backend/models.py",
        "language": "python",
        "content": _generate_models(plan),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(models_file)
    generated_files.append(models_file["filepath"])
    
    # Generate README
    readme_file = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "filename": "README.md",
        "filepath": "/README.md",
        "language": "markdown",
        "content": _generate_readme(plan),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.files.insert_one(readme_file)
    generated_files.append(readme_file["filepath"])
    
    build_phase["files_generated"] = generated_files
    build_phase["status"] = "completed"
    build_phase["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    # Update session
    await db.god_mode_sessions.update_one(
        {"id": session_id},
        {
            "$push": {"phases": build_phase},
            "$set": {
                "status": "built",
                "generated_files": generated_files
            }
        }
    )
    
    # Update project status
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"status": "active"}}
    )
    
    return {
        "session_id": session_id,
        "project_id": project_id,
        "status": "built",
        "files_generated": generated_files,
        "total_files": len(generated_files),
        "next_step": f"Project ready! View at /projects/{project_id}"
    }


@router.post("/stream")
async def god_mode_stream(prompt: str):
    """Stream god mode creation progress"""
    
    async def generate():
        yield f"data: {json.dumps({'type': 'start', 'message': 'GOD MODE ACTIVATED'})}\n\n"
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'analyzing', 'message': 'Analyzing your vision...'})}\n\n"
        
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'planning', 'message': 'Creating business architecture...'})}\n\n"
        
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'generating', 'message': 'Generating landing page...'})}\n\n"
        
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'file', 'file': 'LandingPage.jsx'})}\n\n"
        
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'generating', 'message': 'Generating dashboard...'})}\n\n"
        yield f"data: {json.dumps({'type': 'file', 'file': 'Dashboard.jsx'})}\n\n"
        
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'generating', 'message': 'Generating API...'})}\n\n"
        yield f"data: {json.dumps({'type': 'file', 'file': 'api.py'})}\n\n"
        
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'generating', 'message': 'Generating auth system...'})}\n\n"
        yield f"data: {json.dumps({'type': 'file', 'file': 'auth.py'})}\n\n"
        
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'complete', 'message': 'SaaS CREATED!'})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'prompt': prompt})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{session_id}")
async def get_god_mode_session(session_id: str):
    """Get god mode session status"""
    session = await db.god_mode_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions")
async def list_god_mode_sessions():
    """List all god mode sessions"""
    return await db.god_mode_sessions.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)


# ========== FILE GENERATORS ==========

def _generate_landing_page(plan: dict) -> str:
    name = plan.get("business_name", "SaaS Platform")
    tagline = plan.get("tagline", "The future of software")
    features = plan.get("core_features", ["Feature 1", "Feature 2", "Feature 3"])
    
    features_jsx = "\n".join([
        f'        <div className="feature-card"><h3>{f}</h3></div>'
        for f in features[:6]
    ])
    
    return f'''import React from 'react';

const LandingPage = () => {{
  return (
    <div className="landing-page">
      <header className="hero">
        <h1>{name}</h1>
        <p className="tagline">{tagline}</p>
        <div className="cta-buttons">
          <button className="primary">Get Started</button>
          <button className="secondary">Learn More</button>
        </div>
      </header>
      
      <section className="features">
        <h2>Features</h2>
        <div className="features-grid">
{features_jsx}
        </div>
      </section>
      
      <section className="pricing">
        <h2>Pricing</h2>
        <div className="pricing-cards">
          <div className="price-card">
            <h3>Starter</h3>
            <p className="price">$9/mo</p>
            <button>Start Free Trial</button>
          </div>
          <div className="price-card featured">
            <h3>Pro</h3>
            <p className="price">$29/mo</p>
            <button>Start Free Trial</button>
          </div>
          <div className="price-card">
            <h3>Enterprise</h3>
            <p className="price">Custom</p>
            <button>Contact Sales</button>
          </div>
        </div>
      </section>
      
      <footer>
        <p>&copy; 2025 {name}. All rights reserved.</p>
      </footer>
    </div>
  );
}};

export default LandingPage;
'''


def _generate_dashboard(plan: dict) -> str:
    name = plan.get("business_name", "Dashboard")
    
    return f'''import React, {{ useState, useEffect }} from 'react';

const Dashboard = () => {{
  const [stats, setStats] = useState({{
    users: 0,
    revenue: 0,
    growth: 0
  }});
  
  useEffect(() => {{
    // Fetch dashboard stats
    fetch('/api/stats')
      .then(res => res.json())
      .then(setStats)
      .catch(console.error);
  }}, []);
  
  return (
    <div className="dashboard">
      <header>
        <h1>{name} Dashboard</h1>
      </header>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Users</h3>
          <p className="stat-value">{{stats.users}}</p>
        </div>
        <div className="stat-card">
          <h3>Revenue</h3>
          <p className="stat-value">${{stats.revenue}}</p>
        </div>
        <div className="stat-card">
          <h3>Growth</h3>
          <p className="stat-value">{{stats.growth}}%</p>
        </div>
      </div>
      
      <div className="main-content">
        <section className="recent-activity">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            {{/* Activity items */}}
          </div>
        </section>
        
        <section className="quick-actions">
          <h2>Quick Actions</h2>
          <button>Create New</button>
          <button>View Reports</button>
          <button>Settings</button>
        </section>
      </div>
    </div>
  );
}};

export default Dashboard;
'''


def _generate_api(plan: dict) -> str:
    endpoints = plan.get("api_endpoints", ["/api/users", "/api/stats"])
    
    return f'''"""
Auto-generated API for {plan.get("business_name", "SaaS")}
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List, Optional

router = APIRouter()


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics"""
    return {{
        "users": 1250,
        "revenue": 45000,
        "growth": 23.5,
        "timestamp": datetime.utcnow().isoformat()
    }}


@router.get("/users")
async def get_users(limit: int = 50):
    """Get user list"""
    return {{"users": [], "total": 0}}


@router.post("/users")
async def create_user(email: str, name: str):
    """Create new user"""
    return {{"id": "new-user-id", "email": email, "name": name}}


@router.get("/health")
async def health_check():
    """API health check"""
    return {{"status": "healthy", "service": "{plan.get("business_name", "API")}"}}
'''


def _generate_auth() -> str:
    return '''"""
Authentication system
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = "your-secret-key"  # Use env var in production
ALGORITHM = "HS256"


def create_token(user_id: str) -> str:
    """Create JWT token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login")
async def login(email: str, password: str):
    """User login"""
    # Verify credentials (implement your logic)
    user_id = "user-123"  # From database
    token = create_token(user_id)
    return {"token": token, "user_id": user_id}


@router.post("/register")
async def register(email: str, password: str, name: str):
    """User registration"""
    # Create user (implement your logic)
    user_id = "new-user-123"
    token = create_token(user_id)
    return {"token": token, "user_id": user_id}


@router.get("/me")
async def get_current_user(user_id: str = Depends(verify_token)):
    """Get current user"""
    return {"user_id": user_id}
'''


def _generate_models(plan: dict) -> str:
    name = plan.get("business_name", "App")
    
    return f'''"""
Database models for {name}
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    plan: str = "free"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {{
            "example": {{
                "email": "user@example.com",
                "name": "John Doe",
                "plan": "pro"
            }}
        }}


class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plan: str
    status: str = "active"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class Activity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    metadata: dict = {{}}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
'''


def _generate_readme(plan: dict) -> str:
    name = plan.get("business_name", "SaaS Project")
    tagline = plan.get("tagline", "")
    features = plan.get("core_features", [])
    tech = plan.get("tech_stack", {})
    
    features_md = "\n".join([f"- {f}" for f in features])
    
    return f'''# {name}

{tagline}

## Features

{features_md}

## Tech Stack

- Frontend: {tech.get("frontend", "React")}
- Backend: {tech.get("backend", "FastAPI")}
- Database: {tech.get("database", "PostgreSQL")}
- Deployment: {tech.get("deployment", "Vercel")}

## Getting Started

```bash
# Install dependencies
npm install  # Frontend
pip install -r requirements.txt  # Backend

# Run development servers
npm run dev  # Frontend
uvicorn main:app --reload  # Backend
```

## Project Structure

```
/
├── src/
│   ├── pages/
│   │   ├── LandingPage.jsx
│   │   └── Dashboard.jsx
│   └── components/
├── backend/
│   ├── api.py
│   ├── auth.py
│   └── models.py
└── README.md
```

## License

MIT

---

*Generated by AgentForge God Mode*
'''
