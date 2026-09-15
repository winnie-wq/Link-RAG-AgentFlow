import sqlite3


def query_articles(
    keyword: str,
    limit: int = 5,
):

    limit = min(
        max(limit, 1),
        20,
    )

    connection = sqlite3.connect("data/articles.db")

    cursor = connection.execute(
        """
        SELECT
            external_id,
            title,
            content
        FROM articles
        WHERE
            title LIKE ?
            OR content LIKE ?
        LIMIT ?
        """,
        (
            f"%{keyword}%",
            f"%{keyword}%",
            limit,
        ),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "external_id": row[0],
            "title": row[1],
            "content": row[2],
        }
        for row in rows
    ]
