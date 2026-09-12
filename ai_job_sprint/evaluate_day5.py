import asyncio
import csv
from pathlib import Path

from app.services.rag_optimized_service import (
    OptimizedRAGService,
)

TEST_CASES = [
    '''
    {
        "question": "员工入职满一年有多少天年假？",
        "expected_keyword": "5天",
    },
    {
        "question": "工作一年以后可以休几天带薪假？",
        "expected_keyword": "5天",
    },
    {
        "question": "高铁出差能报销吗？",
        "expected_keyword": "二等座",
    },
    {
        "question": "公司允许报销哪种高铁座位？",
        "expected_keyword": "二等座",
    },
    {
        "question": "住宿最多能报多少钱？",
        "expected_keyword": "500",
    },
    {
        "question": "AI部门2025年收入是多少？",
        "expected_keyword": "100",
    },
    {
        "question": "2026年AI部门收入？",
        "expected_keyword": "135",
    },
    {
        "question": "AI部门两年的收入情况",
        "expected_keyword": "135",
    },
    {
        "question": "员工年终奖是多少？",
        "expected_keyword": None,
    },
    {
        "question": "公司有没有免费午餐？",
        "expected_keyword": None,
    },
    {
        "question": "带薪休假的规定",
        "expected_keyword": "年假",
    },
    {
        "question": "员工满五年后的假期制度",
        "expected_keyword": "10",
    },
    '''
    {
        "question": "差旅住宿标准",
        "expected_keyword": "500",
    },
    {
        "question": "AI部门去年的收入",
        "expected_keyword": "100",
    },
    {
        "question": "因公出差交通费规定",
        "expected_keyword": "高铁",
    },
]


MODES = [
    "vector",
    "hybrid",
    "hybrid_rerank",
]


async def main():

    rag = OptimizedRAGService()

    rag.index_text_document(
        file_path="data/company.md",
        chunk_size=100,
        overlap=20,
    )

    rows = []

    for test_case in TEST_CASES:

        print(
            type(test_case),
            test_case,
        )

        question = test_case["question"]

        expected = test_case["expected_keyword"]

        for mode in MODES:

            result = await rag.answer(
                question=question,
                mode=mode,
                top_k=3,
            )

            answer = result["answer"]

            if expected is None:

                # 文档不存在答案时
                # 人工检查模型有没有正确拒答
                correct = ""

            else:

                correct = expected in answer

            rows.append(
                {
                    "question": question,
                    "mode": mode,
                    "answer": answer,
                    "expected_keyword": expected or "",
                    "auto_correct": correct,
                }
            )

    Path("reports").mkdir(exist_ok=True)

    csv_path = "reports/" "day5_rag_eval.csv"

    with open(
        csv_path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()

        writer.writerows(rows)

    print(f"评测完成：{csv_path}")


if __name__ == "__main__":

    asyncio.run(main())
