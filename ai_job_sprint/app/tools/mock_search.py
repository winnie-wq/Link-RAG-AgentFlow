MOCK_DATA = [
    {
        "title": "FastAPI 入门",
        "content": "FastAPI 是一个现代、高性能的 Python Web 框架。",
    },
    {
        "title": "RAG 基础",
        "content": "RAG 通过检索外部知识增强大模型回答。",
    },
    {
        "title": "Tool Calling",
        "content": "Tool Calling 允许模型选择并调用外部工具。",
    },
]


def mock_search(query: str):

    query = query.strip().lower()

    if not query:
        raise ValueError("query 不能为空")

    results = []

    for item in MOCK_DATA:

        text = (
            item["title"]
            + " "
            + item["content"]
        ).lower()

        if query in text:

            results.append(item)

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }