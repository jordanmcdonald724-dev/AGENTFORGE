"""
Preview Routes
==============
Routes for project preview functionality.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
from core.database import db

router = APIRouter(tags=["preview"])


@router.get("/projects/{project_id}/preview")
async def get_project_preview(project_id: str):
    """Get HTML preview of a project"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    
    html_file = next((f for f in files if f.get("filepath", "").endswith(".html")), None)
    css_files = [f for f in files if f.get("filepath", "").endswith(".css")]
    js_files = [f for f in files if f.get("filepath", "").endswith(".js")]
    
    if not html_file:
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project['name']} Preview</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: #1a1a1a;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 40px;
        }}
        h1 {{ color: #60a5fa; }}
        p {{ color: #9ca3af; }}
        .files {{ margin-top: 20px; text-align: left; max-width: 400px; }}
        .file {{ background: #27272a; padding: 8px 12px; margin: 4px 0; border-radius: 4px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{project['name']}</h1>
        <p>{project.get('description', 'No description')}</p>
        <p>Type: {project['type']}</p>
        <div class="files">
            <h3>Project Files ({len(files)})</h3>
            {''.join([f'<div class="file">{f.get("filepath", "unknown")}</div>' for f in files[:15]])}
        </div>
    </div>
</body>
</html>"""
    else:
        html_content = html_file.get("content", "")
        
        if css_files:
            css_content = "\n".join([f.get("content", "") for f in css_files])
            if "</head>" in html_content:
                html_content = html_content.replace("</head>", f"<style>{css_content}</style></head>")
        
        if js_files:
            js_content = "\n".join([f.get("content", "") for f in js_files])
            if "</body>" in html_content:
                html_content = html_content.replace("</body>", f"<script>{js_content}</script></body>")
    
    return HTMLResponse(content=html_content)


@router.get("/projects/{project_id}/preview-data")
async def get_preview_data(project_id: str):
    """Get preview data for a project"""
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = await db.files.find({"project_id": project_id}, {"_id": 0}).to_list(500)
    images = await db.images.find({"project_id": project_id}, {"_id": 0}).to_list(100)
    
    return {
        "project": project,
        "files": [{
            "id": f["id"],
            "filepath": f.get("filepath"),
            "language": f.get("language"),
            "lines": len(f.get("content", "").split("\n"))
        } for f in files],
        "images": [{
            "id": img["id"],
            "url": img.get("url"),
            "prompt": img.get("prompt", "")[:50]
        } for img in images],
        "stats": {
            "total_files": len(files),
            "total_lines": sum(len(f.get("content", "").split("\n")) for f in files),
            "total_images": len(images)
        }
    }
