import math
import re

from collections import Counter


class SimpleEmbedding:

    def __init__(
        self,
        vocabulary: list[str],
    ):

        self.vocabulary = vocabulary

    @staticmethod
    def tokenize(
        text: str,
    ):

        text = text.lower()

        return re.findall(
            r"[\u4e00-\u9fff]|[a-z0-9]+",
            text,
        )

    @classmethod
    def build(
        cls,
        texts: list[str],
    ):

        vocabulary = set()

        for text in texts:

            vocabulary.update(cls.tokenize(text))

        return cls(sorted(vocabulary))

    def embed(
        self,
        text: str,
    ):

        counter = Counter(self.tokenize(text))

        return [
            float(
                counter.get(
                    word,
                    0,
                )
            )
            for word in self.vocabulary
        ]


def cosine_similarity(
    vector_a,
    vector_b,
):

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    norm_a = math.sqrt(sum(a * a for a in vector_a))

    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
