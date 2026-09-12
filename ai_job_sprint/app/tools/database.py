import sqlite3

DB_PATH = "tool_demo.db"


def init_database():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
        """)

    cursor.execute("""
        SELECT COUNT(*)
        FROM employees
        """)

    count = cursor.fetchone()[0]

    if count == 0:

        cursor.executemany(
            """
            INSERT INTO employees (
                name,
                department
            )
            VALUES (?, ?)
            """,
            [
                ("Alice", "AI"),
                ("Bob", "Backend"),
                ("Charlie", "AI"),
            ],
        )

    connection.commit()
    connection.close()


def database_query(
    department: str,
):

    if not department:
        raise ValueError("department 不能为空")

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, department
        FROM employees
        WHERE department = ?
        """,
        (department,),
    )

    rows = cursor.fetchall()

    connection.close()

    employees = []

    for row in rows:

        employees.append(
            {
                "id": row[0],
                "name": row[1],
                "department": row[2],
            }
        )

    return {
        "department": department,
        "employees": employees,
    }
