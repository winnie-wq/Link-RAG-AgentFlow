import pandas as pd


def clean_posts(
    raw_data: list[dict],
):

    df = pd.DataFrame(raw_data)

    # ---------------------------------------------
    # 统一列名
    # ---------------------------------------------

    df = df.rename(
        columns={
            "id": "external_id",
            "body": "content",
            "userId": "author_id",
        }
    )

    # ---------------------------------------------
    # 缺失值
    # ---------------------------------------------

    df["title"] = df["title"].fillna("")

    df["content"] = df["content"].fillna("")

    # ---------------------------------------------
    # 清理空格
    # ---------------------------------------------

    df["title"] = df["title"].astype(str).str.strip()

    df["content"] = df["content"].astype(str).str.strip()

    # ---------------------------------------------
    # 去重
    # ---------------------------------------------

    df = df.drop_duplicates(subset=["external_id"])

    # ---------------------------------------------
    # 删除无正文记录
    # ---------------------------------------------

    df = df[df["content"] != ""]

    return df[
        [
            "external_id",
            "title",
            "content",
            "author_id",
        ]
    ]
