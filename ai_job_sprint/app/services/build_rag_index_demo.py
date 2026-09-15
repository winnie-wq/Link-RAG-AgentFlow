from app.core.runtime import rag_service


def main():

    result = rag_service.index_text_document(
        file_path="data/knowledge.txt",
        chunk_size=500,
        overlap=100,
    )

    print("索引建立成功！")
    print("来源：", result["source"])
    print("Chunk 数量：", result["chunk_count"])


if __name__ == "__main__":
    main()
