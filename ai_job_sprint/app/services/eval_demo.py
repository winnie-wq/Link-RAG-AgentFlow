import time

from volcenginesdkarkruntime import Ark

from app.core.config import ARK_API_KEY, ARK_MODEL

QUESTIONS = [
    "什么是 RAG？",
    "什么是 Agent？",
    "什么是 MCP？",
]


client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ARK_API_KEY,
)


def ask(question: str) -> str:

    response = client.responses.create(
        model=ARK_MODEL,
        input=question,
    )

    for item in response.output:

        if item.type != "message":
            continue

        for content in item.content:

            if content.type == "output_text":
                return content.text

    return ""


def evaluate():

    success_count = 0
    total_time = 0

    for question in QUESTIONS:

        start = time.perf_counter()

        try:

            answer = ask(question)

            latency = time.perf_counter() - start

            success_count += 1
            total_time += latency

            print("问题：", question)
            print("答案：", answer)
            print("耗时：", round(latency, 3), "秒")

        except Exception as exc:

            print("问题：", question)
            print("执行失败：", repr(exc))

        print("-" * 40)

    success_rate = success_count / len(QUESTIONS)

    print("测试数量：", len(QUESTIONS))
    print("成功数量：", success_count)
    print("成功率：", round(success_rate * 100, 2), "%")

    if success_count:
        print(
            "平均延迟：",
            round(total_time / success_count, 3),
            "秒",
        )


if __name__ == "__main__":
    evaluate()
