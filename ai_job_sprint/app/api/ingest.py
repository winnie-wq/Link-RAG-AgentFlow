import logging

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.core.runtime import (
    rag_service,
)

from app.schemas.ingest import (
    IngestRequest,
    IngestResponse,
)

from app.services.ingest_service import (
    IngestService,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["Data Ingestion"],
)


ingest_service = IngestService(rag=rag_service)


@router.post(
    "/ingest",
    response_model=IngestResponse,
)
async def ingest(
    request: IngestRequest,
):

    try:

        return ingest_service.ingest(
            source_url=request.source_url,
            pages=request.pages,
        )

    except Exception as exc:

        logger.exception("Ingest failed")

        raise HTTPException(
            status_code=500,
            detail=(f"Ingest 失败: " f"{type(exc).__name__}: " f"{str(exc)}"),
        ) from exc
