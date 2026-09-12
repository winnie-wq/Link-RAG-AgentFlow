import math
import re
from collections import Counter

# =========================================================
# 测试文档
# =========================================================

DOCUMENTS = [
    {
        "chunk_id": "doc-1",
        "text": "员工入职满一年后，可以享受5天带薪年假。",
    },
    {
        "chunk_id": "doc-2",
        "text": "员工因公出差时，高铁二等座可以正常报销。",
    },
    {
        "chunk_id": "doc-3",
        "text": "FastAPI 参数验证失败时可能返回 HTTP 422。",
    },
    {
        "chunk_id": "doc-4",
        "text": "FastAPI 是一个现代 Python Web 框架。",
    },
]


# =========================================================
# 1. Tokenizer
# =========================================================


def tokenize(text: str):

    text = text.lower()

    # 英文、数字
    english_tokens = re.findall(
        r"[a-z0-9_]+",
        text,
    )

    # 中文
    chinese_parts = re.findall(
        r"[\u4e00-\u9fff]+",
        text,
    )

    chinese_tokens = []

    for part in chinese_parts:

        # 单字
        chinese_tokens.extend(list(part))

        # 二元词组
        for i in range(len(part) - 1):
            chinese_tokens.append(part[i : i + 2])

    return english_tokens + chinese_tokens


# =========================================================
# 2. 最小 BM25
# =========================================================


class BM25:

    def __init__(
        self,
        documents,
        k1=1.5,
        b=0.75,
    ):

        self.documents = documents

        self.k1 = k1
        self.b = b

        self.tokenized_docs = [tokenize(item["text"]) for item in documents]

        self.doc_lengths = [len(tokens) for tokens in self.tokenized_docs]

        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)

        self.doc_freq = Counter()

        for tokens in self.tokenized_docs:

            unique_tokens = set(tokens)

            for token in unique_tokens:
                self.doc_freq[token] += 1

    def _idf(
        self,
        token,
    ):

        total_docs = len(self.documents)

        df = self.doc_freq.get(
            token,
            0,
        )

        return math.log(1 + (total_docs - df + 0.5) / (df + 0.5))

    def score_document(
        self,
        query,
        doc_index,
    ):

        query_tokens = tokenize(query)

        doc_tokens = self.tokenized_docs[doc_index]

        frequencies = Counter(doc_tokens)

        doc_length = self.doc_lengths[doc_index]

        score = 0.0

        for token in query_tokens:

            tf = frequencies.get(
                token,
                0,
            )

            if tf == 0:
                continue

            idf = self._idf(token)

            numerator = tf * (self.k1 + 1)

            denominator = tf + self.k1 * (
                1 - self.b + self.b * doc_length / self.avg_doc_length
            )

            score += idf * numerator / denominator

        return score

    def search(
        self,
        query,
        top_k=3,
    ):

        results = []

        for index, document in enumerate(self.documents):

            score = self.score_document(
                query,
                index,
            )

            results.append(
                {
                    **document,
                    "score": score,
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:top_k]


# =========================================================
# 3. 教学版 Vector Search
# =========================================================


def build_vocabulary(
    documents,
    query,
):

    words = set()

    for document in documents:

        words.update(tokenize(document["text"]))

    words.update(tokenize(query))

    return sorted(words)


def embed(
    text,
    vocabulary,
):

    counter = Counter(tokenize(text))

    return [
        float(
            counter.get(
                word,
                0,
            )
        )
        for word in vocabulary
    ]


def cosine_similarity(
    a,
    b,
):

    dot = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))

    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def vector_search(
    query,
    documents,
    top_k=3,
):

    vocabulary = build_vocabulary(
        documents,
        query,
    )

    query_vector = embed(
        query,
        vocabulary,
    )

    results = []

    for document in documents:

        doc_vector = embed(
            document["text"],
            vocabulary,
        )

        score = cosine_similarity(
            query_vector,
            doc_vector,
        )

        results.append(
            {
                **document,
                "score": score,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]


# =========================================================
# 4. RRF Fusion
# =========================================================


def rrf_fusion(
    bm25_results,
    vector_results,
    k=60,
):

    scores = {}
    documents = {}

    # BM25 排名
    for rank, item in enumerate(
        bm25_results,
        start=1,
    ):

        chunk_id = item["chunk_id"]

        documents[chunk_id] = item

        scores[chunk_id] = scores.get(
            chunk_id,
            0,
        ) + 1 / (k + rank)

    # Vector 排名
    for rank, item in enumerate(
        vector_results,
        start=1,
    ):

        chunk_id = item["chunk_id"]

        documents[chunk_id] = item

        scores[chunk_id] = scores.get(
            chunk_id,
            0,
        ) + 1 / (k + rank)

    results = []

    for chunk_id, score in scores.items():

        item = dict(documents[chunk_id])

        item["rrf_score"] = score

        results.append(item)

    results.sort(
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return results


# =========================================================
# Demo
# =========================================================

if __name__ == "__main__":

    query = "FastAPI 422 错误"

    bm25 = BM25(DOCUMENTS)

    bm25_results = bm25.search(
        query,
        top_k=4,
    )

    vector_results = vector_search(
        query,
        DOCUMENTS,
        top_k=4,
    )

    hybrid_results = rrf_fusion(
        bm25_results,
        vector_results,
    )

    print("\n========== BM25 ==========")

    for item in bm25_results:

        print(
            round(
                item["score"],
                4,
            ),
            item["text"],
        )

    print("\n========== Vector ==========")

    for item in vector_results:

        print(
            round(
                item["score"],
                4,
            ),
            item["text"],
        )

    print("\n========== Hybrid RRF ==========")

    for item in hybrid_results:

        print(
            round(
                item["rrf_score"],
                6,
            ),
            item["text"],
        )
