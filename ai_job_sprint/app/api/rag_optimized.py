import logging

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.rag_optimized import (
    OptimizedRAGRequest,
    OptimizedRAGResponse,
)

from app.services.rag_optimized_service import (
    OptimizedRAGService,
)


from app.core.runtime import (
    rag_service,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["Optimized RAG"],
)


@router.post(
    "/rag-optimized/index",
)
async def index_documents():

    try:

        return rag_service.index_text_document(
            file_path="data/company.md",
            chunk_size=100,
            overlap=20,
        )

    except Exception as exc:

        logger.exception("Optimized RAG " "index failed")

        raise HTTPException(
            status_code=500,
            detail="建立 RAG 索引失败",
        ) from exc


@router.post(
    "/rag-optimized/ask",
    response_model=OptimizedRAGResponse,
)
async def ask(
    request: OptimizedRAGRequest,
):

    try:

        if not rag_service.is_ready():

            raise HTTPException(
                status_code=400,
                detail=("RAG 索引尚未建立，" "请先调用 " "POST /rag-optimized/index"),
            )

        return await rag_service.answer(
            question=request.question,
            mode=request.mode,
            top_k=request.top_k,
        )

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception("Optimized RAG request failed")

        raise HTTPException(
            status_code=500,
            detail="RAG 查询失败",
        ) from exc
