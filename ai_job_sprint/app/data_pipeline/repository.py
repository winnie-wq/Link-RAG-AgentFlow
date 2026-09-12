import hashlib
import sqlite3


class ArticleRepository:

    def __init__(
        self,
        db_path: str = "data/articles.db",
    ):

        self.db_path = db_path

        self._create_table()

    def _connect(self):

        return sqlite3.connect(self.db_path)

    # =====================================================
    # 建表
    # =====================================================

    def _create_table(self):

        connection = self._connect()

        connection.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                external_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id TEXT,
                content_hash TEXT NOT NULL
            )
            """)

        connection.commit()

        connection.close()

    # =====================================================
    # Hash
    # =====================================================

    def _hash_content(
        self,
        title,
        content,
    ):

        text = title + "\n" + content

        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # =====================================================
    # Upsert
    # =====================================================

    def upsert(
        self,
        row,
    ):

        external_id = str(row["external_id"])

        content_hash = self._hash_content(
            row["title"],
            row["content"],
        )

        connection = self._connect()

        cursor = connection.execute(
            """
            SELECT content_hash
            FROM articles
            WHERE external_id = ?
            """,
            (external_id,),
        )

        existing = cursor.fetchone()

        # 新数据
        if existing is None:

            connection.execute(
                """
                INSERT INTO articles (
                    external_id,
                    title,
                    content,
                    author_id,
                    content_hash
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    external_id,
                    row["title"],
                    row["content"],
                    str(row["author_id"]),
                    content_hash,
                ),
            )

            status = "inserted"

        # 完全没变化
        elif existing[0] == content_hash:

            status = "unchanged"

        # 内容发生变化
        else:

            connection.execute(
                """
                UPDATE articles
                SET
                    title = ?,
                    content = ?,
                    author_id = ?,
                    content_hash = ?
                WHERE external_id = ?
                """,
                (
                    row["title"],
                    row["content"],
                    str(row["author_id"]),
                    content_hash,
                    external_id,
                ),
            )

            status = "updated"

        connection.commit()

        connection.close()

        return status
