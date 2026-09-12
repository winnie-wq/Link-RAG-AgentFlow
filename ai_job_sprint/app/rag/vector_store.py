from app.rag.embedding import (
    cosine_similarity,
)


class InMemoryVectorStore:

    def __init__(self):

        self.records = []

    # =============================================
    # CREATE
    # =============================================

    def add(
        self,
        *,
        chunk_id: str,
        text: str,
        vector: list[float],
        metadata: dict,
    ):

        self.records.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "vector": vector,
                "metadata": metadata,
            }
        )

    # =============================================
    # READ
    # =============================================

    def get(
        self,
        chunk_id: str,
    ):

        for record in self.records:

            if record["chunk_id"] == chunk_id:
                return record

        return None

    # =============================================
    # UPDATE
    # =============================================

    def update(
        self,
        chunk_id: str,
        **updates,
    ):

        record = self.get(chunk_id)

        if record is None:
            return False

        record.update(updates)

        return True

    # =============================================
    # DELETE
    # =============================================

    def delete(
        self,
        chunk_id: str,
    ):

        before = len(self.records)

        self.records = [
            record for record in self.records if (record["chunk_id"] != chunk_id)
        ]

        return len(self.records) < before

    # =============================================
    # VECTOR SEARCH
    # =============================================

    def search(
        self,
        query_vector,
        top_k: int = 3,
    ):

        results = []

        for record in self.records:

            score = cosine_similarity(
                query_vector,
                record["vector"],
            )

            results.append(
                {
                    **record,
                    "score": score,
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]
