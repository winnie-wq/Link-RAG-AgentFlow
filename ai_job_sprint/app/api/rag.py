import logging

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.rag import (
    RAGRequest,
    RAGResponse,
)

from app.services.rag_service import (
    RAGService,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["RAG"],
)


rag = RAGService()


@router.post(
    "/rag/index",
)
async def index_documents():

    try:

        result = rag.index_text_document(
            file_path="data/company.md",
            chunk_size=100,
            overlap=20,
        )

        return result

    except Exception as exc:

        logger.exception("RAG index failed")

        raise HTTPException(
            status_code=500,
            detail="RAG 建立索引失败",
        ) from exc


@router.post(
    "/rag/ask",
    response_model=RAGResponse,
)
async def ask_rag(
    request: RAGRequest,
):

    try:

        result = await rag.answer(
            question=request.question,
            top_k=request.top_k,
        )

        return result

    except Exception as exc:

        logger.exception("RAG request failed")

        raise HTTPException(
            status_code=500,
            detail="RAG 执行失败",
        ) from exc
