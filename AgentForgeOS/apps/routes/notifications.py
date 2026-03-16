"""
Notification Routes
===================
Routes for managing project notifications (email, Discord).
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional
from engine.core.database import db
from services.utils import serialize_doc
import os
import httpx

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/{project_id}/settings")
async def get_notification_settings(project_id: str):
    """Get notification settings for a project"""
    settings = await db.notification_settings.find_one({"project_id": project_id}, {"_id": 0})
    
    if not settings:
        settings = {
            "id": f"ns-{project_id[:8]}",
            "project_id": project_id,
            "email_enabled": False,
            "email_address": None,
            "discord_enabled": False,
            "discord_webhook_url": None,
            "notify_on_complete": True,
            "notify_on_milestones": True,
            "notify_on_errors": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notification_settings.insert_one(settings)
    
    return settings


@router.post("/{project_id}/settings")
async def update_notification_settings(
    project_id: str,
    email_enabled: bool = None,
    email_address: str = None,
    discord_enabled: bool = None,
    discord_webhook_url: str = None,
    notify_on_complete: bool = None,
    notify_on_milestones: bool = None,
    notify_on_errors: bool = None
):
    """Update notification settings for a project"""
    updates = {}
    if email_enabled is not None:
        updates["email_enabled"] = email_enabled
    if email_address is not None:
        updates["email_address"] = email_address
    if discord_enabled is not None:
        updates["discord_enabled"] = discord_enabled
    if discord_webhook_url is not None:
        updates["discord_webhook_url"] = discord_webhook_url
    if notify_on_complete is not None:
        updates["notify_on_complete"] = notify_on_complete
    if notify_on_milestones is not None:
        updates["notify_on_milestones"] = notify_on_milestones
    if notify_on_errors is not None:
        updates["notify_on_errors"] = notify_on_errors
    
    if updates:
        await db.notification_settings.update_one(
            {"project_id": project_id},
            {"$set": updates},
            upsert=True
        )
    
    return await db.notification_settings.find_one({"project_id": project_id}, {"_id": 0})


@router.post("/{project_id}/test")
async def test_notifications(project_id: str, notification_type: str = "all"):
    """Test notification channels"""
    settings = await db.notification_settings.find_one({"project_id": project_id}, {"_id": 0})
    if not settings:
        raise HTTPException(status_code=404, detail="Notification settings not found")
    
    results = {"email": None, "discord": None}
    
    if notification_type in ["all", "discord"] and settings.get("discord_enabled"):
        webhook_url = settings.get("discord_webhook_url") or os.environ.get("DISCORD_WEBHOOK_URL")
        if webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        webhook_url,
                        json={
                            "content": "🧪 **AgentForge Test Notification**\nThis is a test message from your project.",
                            "embeds": [{
                                "title": "Test Notification",
                                "description": f"Project ID: {project_id}",
                                "color": 5814783,
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }]
                        }
                    )
                    results["discord"] = "sent" if response.status_code == 204 else f"failed: {response.status_code}"
            except Exception as e:
                results["discord"] = f"error: {str(e)}"
        else:
            results["discord"] = "no webhook configured"
    
    if notification_type in ["all", "email"] and settings.get("email_enabled"):
        email = settings.get("email_address")
        if email:
            sendgrid_key = os.environ.get("SENDGRID_API_KEY")
            resend_key = os.environ.get("RESEND_API_KEY")
            
            if sendgrid_key:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://api.sendgrid.com/v3/mail/send",
                            headers={
                                "Authorization": f"Bearer {sendgrid_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "personalizations": [{"to": [{"email": email}]}],
                                "from": {"email": "notifications@agentforge.ai", "name": "AgentForge"},
                                "subject": "🧪 Test Notification from AgentForge",
                                "content": [{"type": "text/plain", "value": f"This is a test notification for project {project_id}."}]
                            }
                        )
                        results["email"] = "sent" if response.status_code == 202 else f"failed: {response.status_code}"
                except Exception as e:
                    results["email"] = f"error: {str(e)}"
            elif resend_key:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://api.resend.com/emails",
                            headers={
                                "Authorization": f"Bearer {resend_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "from": "AgentForge <notifications@agentforge.ai>",
                                "to": [email],
                                "subject": "🧪 Test Notification from AgentForge",
                                "text": f"This is a test notification for project {project_id}."
                            }
                        )
                        results["email"] = "sent" if response.status_code == 200 else f"failed: {response.status_code}"
                except Exception as e:
                    results["email"] = f"error: {str(e)}"
            else:
                results["email"] = "no email service configured"
        else:
            results["email"] = "no email address set"
    
    notification_record = {
        "project_id": project_id,
        "type": "test",
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.notification_history.insert_one(notification_record)
    
    return results


@router.get("/{project_id}/history")
async def get_notification_history(project_id: str, limit: int = 50):
    """Get notification history for a project"""
    return await db.notification_history.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(limit)


async def send_notification(project_id: str, title: str, message: str, notification_type: str = "info"):
    """Send notification to configured channels (internal helper)"""
    settings = await db.notification_settings.find_one({"project_id": project_id}, {"_id": 0})
    if not settings:
        return
    
    color_map = {
        "success": 5763719,
        "error": 15548997,
        "warning": 16776960,
        "info": 5814783
    }
    
    if settings.get("discord_enabled"):
        webhook_url = settings.get("discord_webhook_url") or os.environ.get("DISCORD_WEBHOOK_URL")
        if webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        webhook_url,
                        json={
                            "embeds": [{
                                "title": title,
                                "description": message,
                                "color": color_map.get(notification_type, 5814783),
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }]
                        }
                    )
            except:
                pass
