from app.rag.bm25 import (
    tokenize,
)


class SimpleReranker:

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 3,
    ):

        query_tokens = set(tokenize(query))

        results = []

        for candidate in candidates:

            document_tokens = set(tokenize(candidate["text"]))

            overlap = query_tokens & document_tokens

            if query_tokens:

                keyword_coverage = len(overlap) / len(query_tokens)

            else:

                keyword_coverage = 0

            hybrid_score = candidate.get(
                "hybrid_score",
                candidate.get(
                    "rrf_score",
                    0,
                ),
            )

            rerank_score = keyword_coverage + hybrid_score

            item = dict(candidate)

            item["rerank_score"] = rerank_score

            results.append(item)

        results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return results[:top_k]
