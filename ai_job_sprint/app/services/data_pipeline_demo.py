import sqlite3

import pandas as pd

# =====================================================
# 1. read_csv
# =====================================================

df = pd.read_csv("data/articles.csv")

print("\n===== 原始数据 =====")
print(df)


# =====================================================
# 2. 缺失值处理 fillna
# =====================================================

df["title"] = df["title"].fillna("未命名文章")

df["content"] = df["content"].fillna("")


# =====================================================
# 3. 去重
# =====================================================

"""
subset只保留第一次出现的那一行，删掉后面重复的行

"""

df = df.drop_duplicates(subset=["id"])


# =====================================================
# 4. apply
#
# 统一文本格式
# =====================================================

"""
1. `str(text)`：强制把输入转成字符串。防止遇到数字 / None，后面 strip 报错
2. `.strip()`：**去掉字符串首尾的空白字符**，包含：开头结尾空格、换行`\n`、制表符`\t`
"""


def clean_text(text):

    return str(text).strip()


df["title"] = df["title"].apply(clean_text)

df["content"] = df["content"].apply(clean_text)


# =====================================================
# 5. 删除没有正文的数据
# =====================================================

df = df[df["content"] != ""]


print("\n===== 清洗后 =====")
print(df)


# =====================================================
# 6. groupby
# =====================================================

"""
**按`category`（文档分类 / 类别）分组**，把相同 category 的行归为一组

`.size()`：统计**每个分组里面一共有多少条记录**（计数）
"""

statistics = df.groupby("category").size()

print("\n===== 分类统计 =====")
print(statistics)


# =====================================================
# 7. SQLite
# =====================================================

connection = sqlite3.connect("data/articles.db")

df.to_sql(
    "articles",
    connection,
    if_exists="replace",
    index=False,
)


# =====================================================
# 8. SQL SELECT / WHERE / ORDER BY / LIMIT
# =====================================================

query = """
SELECT
    id,
    title,
    category
FROM articles
WHERE category = ?
ORDER BY id DESC
LIMIT ?
"""


result = pd.read_sql_query(
    query,
    connection,
    params=("技术", 10),
)

print("\n===== SQL 查询 =====")
print(result)


connection.close()
