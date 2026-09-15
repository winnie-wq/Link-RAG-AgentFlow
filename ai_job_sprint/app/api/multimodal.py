from fastapi import APIRouter, UploadFile, File, Form

from app.services.multimodal_service import MultimodalService

router = APIRouter()

service = MultimodalService()


@router.post("/multimodal/analyze")
async def analyze(
    text: str = Form(...),
    image: UploadFile | None = File(None),
):

    image_bytes = None
    content_type = None

    if image:
        image_bytes = await image.read()
        content_type = image.content_type

    return await service.analyze(
        text=text,
        image_bytes=image_bytes,
        content_type=content_type,
    )
