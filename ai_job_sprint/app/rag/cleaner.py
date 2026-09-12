import re


def clean_text(
    text: str,
) -> str:

    # 统一换行
    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # 多个空格压成一个
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # 三个以上连续换行
    # 压缩成两个
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()
