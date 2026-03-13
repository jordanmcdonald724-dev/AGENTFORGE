from fastapi import APIRouter
from datetime import datetime, timezone
from core.database import db
from core.utils import serialize_doc
from models.base import ProjectPlan
from models.project import PlanApproval

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("")
async def create_plan(plan_data: dict):
    plan = ProjectPlan(**plan_data)
    doc = plan.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.plans.delete_many({"project_id": plan_data['project_id']})
    await db.plans.insert_one(doc)
    return serialize_doc(doc)


@router.get("/{project_id}")
async def get_plan(project_id: str):
    return await db.plans.find_one({"project_id": project_id}, {"_id": 0})


@router.patch("/{project_id}/approve")
async def approve_plan(project_id: str, approval: PlanApproval):
    await db.plans.update_one(
        {"project_id": project_id}, 
        {"$set": {"approved": approval.approved}}
    )
    if approval.approved:
        await db.projects.update_one(
            {"id": project_id}, 
            {"$set": {"phase": "development", "status": "developing"}}
        )
    return {"success": True, "approved": approval.approved}
