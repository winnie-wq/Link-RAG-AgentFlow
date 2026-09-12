from app.rag.bm25 import (
    BM25,
)


class HybridSearcher:

    def __init__(
        self,
        *,
        vector_store,
        embedding,
    ):

        self.vector_store = vector_store

        self.embedding = embedding

    def _rrf_fusion(
        self,
        bm25_results,
        vector_results,
        rrf_k=60,
    ):

        scores = {}
        records = {}

        for rank, item in enumerate(
            bm25_results,
            start=1,
        ):

            chunk_id = item["chunk_id"]

            records[chunk_id] = item

            scores[chunk_id] = scores.get(
                chunk_id,
                0,
            ) + 1 / (rrf_k + rank)

        for rank, item in enumerate(
            vector_results,
            start=1,
        ):

            chunk_id = item["chunk_id"]

            records[chunk_id] = item

            scores[chunk_id] = scores.get(
                chunk_id,
                0,
            ) + 1 / (rrf_k + rank)

        fused = []

        for chunk_id, score in scores.items():

            item = dict(records[chunk_id])

            item["rrf_score"] = score

            fused.append(item)

        fused.sort(
            key=lambda item: item["rrf_score"],
            reverse=True,
        )

        return fused

    def search(
        self,
        *,
        query: str,
        candidate_k: int = 10,
    ):

        # =========================================
        # 1. Vector Search
        # =========================================

        query_vector = self.embedding.embed(query)

        vector_results = self.vector_store.search(
            query_vector=query_vector,
            top_k=candidate_k,
        )

        # =========================================
        # 2. BM25 Search
        # =========================================

        documents = []

        for record in self.vector_store.records:

            documents.append(
                {
                    "chunk_id": record["chunk_id"],
                    "text": record["text"],
                    "metadata": record["metadata"],
                }
            )

        bm25 = BM25(documents)

        bm25_results = bm25.search(
            query,
            top_k=candidate_k,
        )

        # =========================================
        # 3. RRF
        # =========================================

        return self._rrf_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
        )
