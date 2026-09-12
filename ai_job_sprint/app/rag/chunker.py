def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
):

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if overlap < 0:
        raise ValueError("overlap 不能小于 0")

    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    chunks = []

    start = 0

    chunk_id = 0

    while start < len(text):

        end = start + chunk_size

        chunk_text_value = text[start:end]

        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": chunk_text_value,
                "metadata": {
                    "start": start,
                    "end": min(
                        end,
                        len(text),
                    ),
                },
            }
        )

        chunk_id += 1

        start += chunk_size - overlap

    return chunks
