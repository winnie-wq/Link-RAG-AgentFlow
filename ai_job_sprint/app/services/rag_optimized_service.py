import logging

from app.rag.loader import load_document
from app.rag.cleaner import clean_text
from app.rag.chunker import chunk_text
from app.rag.embedding import SimpleEmbedding
from app.rag.vector_store import InMemoryVectorStore
from app.rag.hybrid_search import HybridSearcher
from app.rag.reranker import SimpleReranker
from app.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class OptimizedRAGService:

    def __init__(self):

        # 最终回答阶段使用的 LLM
        self.llm = LLMClient()

        # Day4 手写的内存向量库
        self.store = InMemoryVectorStore()

        # 索引建立之前，没有 Embedding 实例
        self.embedding = None

        # 索引建立之前，没有 HybridSearcher
        self.hybrid_searcher = None

        # Reranker 可以提前创建
        self.reranker = SimpleReranker()

    # =====================================================
    # 检查索引是否已经准备好
    # =====================================================

    def is_ready(self) -> bool:

        return (
            self.embedding is not None
            and self.hybrid_searcher is not None
            and len(self.store.records) > 0
        )

    # =====================================================
    # 建立索引
    #
    # loader
    #   ↓
    # clean
    #   ↓
    # chunk
    #   ↓
    # embed
    #   ↓
    # store
    #   ↓
    # hybrid searcher
    # =====================================================

    def index_text_document(
        self,
        *,
        file_path: str,
        chunk_size: int = 500,
        overlap: int = 100,
    ):

        logger.info(
            "RAG indexing started file=%s",
            file_path,
        )

        # ---------------------------------------------
        # 1. 加载文档
        # ---------------------------------------------

        document = load_document(file_path)

        logger.info(
            "Document loaded " "source=%s type=%s",
            document.get("source"),
            document.get("type"),
        )

        # 当前 OptimizedRAGService
        # 暂时只处理 TXT / Markdown
        if document["type"] != "text":

            raise ValueError("当前版本先支持 TXT / Markdown")

        # ---------------------------------------------
        # 2. 文档清洗
        # ---------------------------------------------

        clean_document = clean_text(document["text"])

        logger.info(
            "Document cleaned " "characters=%s",
            len(clean_document),
        )

        # ---------------------------------------------
        # 3. Chunk
        # ---------------------------------------------

        chunks = chunk_text(
            clean_document,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not chunks:

            raise ValueError("文档切分结果为空")

        logger.info(
            "Chunking completed " "chunks=%s " "chunk_size=%s " "overlap=%s",
            len(chunks),
            chunk_size,
            overlap,
        )

        # ---------------------------------------------
        # 4. 准备所有 Chunk 文本
        # ---------------------------------------------

        texts = [chunk["text"] for chunk in chunks]

        # ---------------------------------------------
        # 5. 建立 Embedding
        #
        # 当前使用 Day4 的教学版 SimpleEmbedding
        # ---------------------------------------------

        self.embedding = SimpleEmbedding.build(texts)

        logger.info("Embedding initialized")

        # ---------------------------------------------
        # 6. 清空旧索引
        #
        # 因为当前是 InMemoryVectorStore
        # 每次重新 index 时直接覆盖
        # ---------------------------------------------

        self.store.records.clear()

        logger.info("Old vector records cleared")

        # ---------------------------------------------
        # 7. Chunk → Vector → Store
        # ---------------------------------------------

        for chunk in chunks:

            vector = self.embedding.embed(chunk["text"])

            chunk_id = f"{document['source']}:" f"{chunk['chunk_id']}"

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

        logger.info(
            "Vector store completed " "records=%s",
            len(self.store.records),
        )

        # ---------------------------------------------
        # 8. 初始化 Hybrid Searcher
        #
        # 它后面会同时使用：
        # Vector Search + BM25 + RRF
        # ---------------------------------------------

        self.hybrid_searcher = HybridSearcher(
            vector_store=self.store,
            embedding=self.embedding,
        )

        logger.info("Hybrid searcher initialized")

        # ---------------------------------------------
        # 9. 建索引完成
        # ---------------------------------------------

        logger.info(
            "RAG indexing completed " "source=%s chunks=%s",
            document["source"],
            len(chunks),
        )

        return {
            "source": document["source"],
            "chunk_count": len(chunks),
            "ready": self.is_ready(),
        }

    # =====================================================
    # Vector Only
    # =====================================================

    def retrieve_vector(
        self,
        *,
        question: str,
        top_k: int = 3,
    ):

        if not self.is_ready():

            raise ValueError("请先建立索引")

        logger.info(
            "Vector retrieval started " "question=%s top_k=%s",
            question,
            top_k,
        )

        query_vector = self.embedding.embed(question)

        results = self.store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

        logger.info(
            "Vector retrieval completed " "results=%s",
            len(results),
        )

        return results

    # =====================================================
    # Hybrid Search
    #
    # BM25 + Vector + RRF
    # =====================================================

    def retrieve_hybrid(
        self,
        *,
        question: str,
        candidate_k: int = 10,
    ):

        if not self.is_ready():

            raise ValueError("请先建立索引")

        logger.info(
            "Hybrid retrieval started " "question=%s candidate_k=%s",
            question,
            candidate_k,
        )

        results = self.hybrid_searcher.search(
            query=question,
            candidate_k=candidate_k,
        )

        logger.info(
            "Hybrid retrieval completed " "results=%s",
            len(results),
        )

        return results

    # =====================================================
    # Hybrid + Rerank
    # =====================================================

    def retrieve_hybrid_rerank(
        self,
        *,
        question: str,
        candidate_k: int = 10,
        top_k: int = 3,
    ):

        logger.info(
            "Hybrid+Rerank retrieval started "
            "question=%s "
            "candidate_k=%s "
            "top_k=%s",
            question,
            candidate_k,
            top_k,
        )

        # 第一步：
        # 先使用 Hybrid Search
        # 获取一批候选文档
        candidates = self.retrieve_hybrid(
            question=question,
            candidate_k=candidate_k,
        )

        # 第二步：
        # 对候选文档重新排序
        results = self.reranker.rerank(
            query=question,
            candidates=candidates,
            top_k=top_k,
        )

        logger.info(
            "Hybrid+Rerank completed " "results=%s",
            len(results),
        )

        return results

    # =====================================================
    # 构建 Prompt
    # =====================================================

    def _build_context_and_sources(
        self,
        retrieved: list[dict],
    ):

        context_blocks = []

        sources = []

        for index, item in enumerate(
            retrieved,
            start=1,
        ):

            metadata = item["metadata"]

            context_blocks.append(
                (
                    f"[资料{index}]\n"
                    f"来源: "
                    f"{metadata['source']}\n"
                    f"Chunk: "
                    f"{metadata['chunk_id']}\n"
                    f"内容:\n"
                    f"{item['text']}"
                )
            )

            retrieval_score = item.get(
                "rerank_score",
                item.get(
                    "rrf_score",
                    item.get(
                        "score",
                        0,
                    ),
                ),
            )

            sources.append(
                {
                    "source": metadata["source"],
                    "chunk_id": metadata["chunk_id"],
                    "retrieval_score": retrieval_score,
                }
            )

        context = "\n\n".join(context_blocks)

        return (
            context,
            sources,
        )

    # =====================================================
    # 生成最终答案
    # =====================================================

    async def answer(
        self,
        *,
        question: str,
        mode: str = "hybrid_rerank",
        top_k: int = 3,
    ):

        if not self.is_ready():

            raise ValueError("请先建立索引")

        logger.info(
            "RAG answer started " "mode=%s question=%s",
            mode,
            question,
        )

        # ---------------------------------------------
        # Vector
        # ---------------------------------------------

        if mode == "vector":

            retrieved = self.retrieve_vector(
                question=question,
                top_k=top_k,
            )

        # ---------------------------------------------
        # Hybrid
        # ---------------------------------------------

        elif mode == "hybrid":

            retrieved = (
                self.retrieve_hybrid(
                    question=question,
                    candidate_k=top_k,
                )
            )[:top_k]

        # ---------------------------------------------
        # Hybrid + Rerank
        # ---------------------------------------------

        elif mode == "hybrid_rerank":

            retrieved = self.retrieve_hybrid_rerank(
                question=question,
                candidate_k=10,
                top_k=top_k,
            )

        # ---------------------------------------------
        # 非法 mode
        # ---------------------------------------------

        else:

            raise ValueError(f"未知检索模式: {mode}")

        if not retrieved:

            raise ValueError("没有检索到任何文档")

        # ---------------------------------------------
        # 构建 Context + Sources
        # ---------------------------------------------

        context, sources = self._build_context_and_sources(retrieved)

        # ---------------------------------------------
        # 构建 RAG Prompt
        # ---------------------------------------------

        prompt = f"""
你是一个企业知识库问答助手。

请严格根据【参考资料】回答。

要求：
1. 不允许编造资料中不存在的信息。
2. 如果资料不足，请明确说“根据当前资料无法确定”。
3. 回答简洁准确。
4. 使用 [资料1]、[资料2] 标注引用。
5. 不要把参考资料之外的知识当作文档事实。

【参考资料】

{context}

【问题】

{question}
"""

        # ---------------------------------------------
        # 调用 Day1 的 LLMClient
        # ---------------------------------------------

        answer = await self.llm.chat(prompt)

        logger.info(
            "RAG answer completed " "mode=%s sources=%s",
            mode,
            len(sources),
        )

        return {
            "answer": answer,
            "sources": sources,
            "mode": mode,
        }
