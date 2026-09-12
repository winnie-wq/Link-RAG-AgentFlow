import math
import re
from collections import Counter

# =========================================================
# 1. 准备几段文档
# =========================================================

documents = [
    "公司员工入职满一年后，可以享受5天带薪年假。",
    "公司差旅报销规定：高铁二等座可以正常报销。",
    "AI部门2025年的收入为100万元，2026年的收入为135万元。",
]


# =========================================================
# 2. 最简单的 tokenizer
#
# 注意：
# 这只是教学 Demo。
# 真正 RAG 后面会换成 Embedding Model。
# =========================================================


def tokenize(text: str):

    text = text.lower()

    tokens = re.findall(
        r"[\u4e00-\u9fff]|[a-z0-9]+",
        text,
    )

    return tokens


# =========================================================
# 3. 建立词表
# =========================================================


def build_vocabulary(texts):

    vocabulary = set()

    for text in texts:

        vocabulary.update(tokenize(text))

    return sorted(vocabulary)


# =========================================================
# 4. 把文本转换成向量
#
# 例如词表：
#
# [年假, 公司, 报销]
#
# 文本：
# 公司年假
#
# ↓
#
# [1, 1, 0]
# =========================================================


def embed(
    text: str,
    vocabulary,
):

    counter = Counter(tokenize(text))

    return [counter.get(word, 0) for word in vocabulary]


# =========================================================
# 5. 余弦相似度
# =========================================================


def cosine_similarity(
    vector_a,
    vector_b,
):

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    norm_a = math.sqrt(sum(a * a for a in vector_a))

    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


# =========================================================
# 6. 检索 Top-k
# =========================================================


def retrieve(
    query: str,
    documents,
    top_k: int = 2,
):

    vocabulary = build_vocabulary(documents + [query])

    query_vector = embed(
        query,
        vocabulary,
    )

    scored_documents = []

    for index, document in enumerate(documents):

        document_vector = embed(
            document,
            vocabulary,
        )

        score = cosine_similarity(
            query_vector,
            document_vector,
        )

        scored_documents.append(
            {
                "chunk_id": index,
                "text": document,
                "score": score,
            }
        )

    scored_documents.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_documents[:top_k]


# =========================================================
# 7. Demo
# =========================================================

if __name__ == "__main__":

    query = "员工有多少天年假？"

    results = retrieve(
        query=query,
        documents=documents,
        top_k=2,
    )

    print(f"问题：{query}")

    print()

    for item in results:

        print(
            "chunk_id:",
            item["chunk_id"],
        )

        print(
            "score:",
            round(
                item["score"],
                4,
            ),
        )

        print(
            "text:",
            item["text"],
        )

        print()
