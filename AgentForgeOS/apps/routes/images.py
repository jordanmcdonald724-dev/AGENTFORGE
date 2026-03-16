from fastapi import APIRouter, HTTPException
from engine.core.database import db
from services.utils import serialize_doc
from models.base import GeneratedImage
from models.project import ImageGenRequest
import fal_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["images"])


async def generate_image_fal(prompt: str, width: int = 1024, height: int = 1024) -> dict:
    """Generate image using fal.ai FLUX"""
    try:
        handler = await fal_client.submit_async(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "image_size": {"width": width, "height": height},
                "num_images": 1
            }
        )
        result = await handler.get()
        if result and result.get("images"):
            return {
                "url": result["images"][0]["url"],
                "width": width,
                "height": height
            }
        return None
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/generate")
async def generate_image(request: ImageGenRequest):
    """Generate an image using fal.ai FLUX"""
    result = await generate_image_fal(request.prompt, request.width, request.height)
    
    if result:
        image = GeneratedImage(
            project_id=request.project_id,
            prompt=request.prompt,
            url=result["url"],
            width=result["width"],
            height=result["height"],
            category=request.category
        )
        doc = image.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.images.insert_one(doc)
        
        return serialize_doc(doc)
    
    raise HTTPException(status_code=500, detail="Image generation failed")


@router.get("")
async def get_images(project_id: str):
    return await db.images.find({"project_id": project_id}, {"_id": 0}).to_list(100)


@router.delete("/{image_id}")
async def delete_image(image_id: str):
    await db.images.delete_one({"id": image_id})
    return {"success": True}
