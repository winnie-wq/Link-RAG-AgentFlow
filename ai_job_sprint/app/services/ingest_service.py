from pathlib import Path

from app.data_pipeline.source_loader import (
    fetch_api_posts,
)

from app.data_pipeline.cleaner import (
    clean_posts,
)

from app.data_pipeline.repository import (
    ArticleRepository,
)

from app.services.rag_optimized_service import (
    OptimizedRAGService,
)


class IngestService:

    def __init__(
        self,
        rag: OptimizedRAGService,
    ):

        self.repository = ArticleRepository()

        self.rag = rag

    def ingest(
        self,
        *,
        source_url: str,
        pages: int = 2,
    ):

        # =============================================
        # 1. Extract
        # =============================================

        raw_data = fetch_api_posts(
            base_url=source_url,
            pages=pages,
        )

        # =============================================
        # 2. Transform
        # =============================================

        df = clean_posts(raw_data)

        counts = {
            "inserted": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
        }

        # =============================================
        # 3. Load SQLite
        # =============================================

        for _, row in df.iterrows():

            try:

                status = self.repository.upsert(row)

                counts[status] += 1

            except Exception:

                counts["failed"] += 1

        # =============================================
        # 4. 导出为 RAG 知识文档
        # =============================================

        output_path = Path("data/ingested_knowledge.md")

        blocks = []

        for _, row in df.iterrows():

            blocks.append((f"# {row['title']}\n\n" f"{row['content']}\n"))

        output_path.write_text(
            "\n\n".join(blocks),
            encoding="utf-8",
        )

        # =============================================
        # 5. 自动更新 RAG Index
        # =============================================

        rag_result = self.rag.index_text_document(
            file_path=str(output_path),
            chunk_size=300,
            overlap=50,
        )

        return {
            **counts,
            "total": len(df),
            "rag": rag_result,
        }
