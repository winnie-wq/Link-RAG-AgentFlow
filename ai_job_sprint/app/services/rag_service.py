from pathlib import Path

from app.rag.loader import (
    load_document,
)

from app.rag.cleaner import (
    clean_text,
)

from app.rag.chunker import (
    chunk_text,
)

from app.rag.embedding import (
    SimpleEmbedding,
)

from app.rag.vector_store import (
    InMemoryVectorStore,
)

from app.services.llm_client import (
    LLMClient,
)


class RAGService:

    def __init__(self):

        self.llm = LLMClient()

        self.store = InMemoryVectorStore()

        self.embedding = None

    # =====================================================
    # Index
    # loader → clean → chunk → embed → store
    # =====================================================

    def index_text_document(
        self,
        *,
        file_path: str,
        chunk_size: int = 500,
        overlap: int = 100,
    ):

        document = load_document(file_path)

        if document["type"] != "text":
            raise ValueError("当前版本先使用 TXT / Markdown")

        clean_document = clean_text(document["text"])

        chunks = chunk_text(
            clean_document,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        texts = [chunk["text"] for chunk in chunks]

        self.embedding = SimpleEmbedding.build(texts)

        for chunk in chunks:

            vector = self.embedding.embed(chunk["text"])

            chunk_id = f"{document['source']}" f":{chunk['chunk_id']}"

            metadata = {
                **chunk["metadata"],
                "source": document["source"],
                "chunk_id": chunk["chunk_id"],
            }

            self.store.add(
                chunk_id=chunk_id,
                text=chunk["text"],
                vector=vector,
                metadata=metadata,
            )

        return {
            "source": document["source"],
            "chunk_count": len(chunks),
        }

    # =====================================================
    # Retrieve
    # =====================================================

    def retrieve(
        self,
        *,
        question: str,
        top_k: int = 3,
    ):

        if self.embedding is None:
            raise ValueError("请先建立文档索引")

        query_vector = self.embedding.embed(question)

        return self.store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

    # =====================================================
    # Generate
    # retrieve → context → LLM
    # =====================================================

    async def answer(
        self,
        *,
        question: str,
        top_k: int = 3,
    ):

        retrieved = self.retrieve(
            question=question,
            top_k=top_k,
        )

        context_blocks = []

        sources = []

        for index, item in enumerate(
            retrieved,
            start=1,
        ):

            source = item["metadata"]["source"]

            chunk_id = item["metadata"]["chunk_id"]

            context_blocks.append(
                (
                    f"[资料{index}]\n"
                    f"来源: {source}\n"
                    f"Chunk: {chunk_id}\n"
                    f"内容:\n{item['text']}"
                )
            )

            sources.append(
                {
                    "source": source,
                    "chunk_id": chunk_id,
                    "score": item["score"],
                }
            )

        context = "\n\n".join(context_blocks)

        prompt = f"""
你是一个基于文档回答问题的助手。

请严格根据【参考资料】回答用户问题。

要求：
1. 不允许编造参考资料中不存在的事实。
2. 如果参考资料不足以回答，请明确说“根据当前资料无法确定”。
3. 回答简洁、准确。
4. 在结尾标注引用，例如：[资料1]。
5. 不要把资料之外的知识当成文档事实。

【参考资料】

{context}

【用户问题】

{question}
"""

        answer = await self.llm.chat(prompt)

        return {
            "answer": answer,
            "sources": sources,
        }
