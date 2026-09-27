import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent
    / "aura_memory.db"
)


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def _column_exists(
    connection,
    table_name: str,
    column_name: str
) -> bool:

    columns = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        column["name"] == column_name
        for column in columns
    )


def initialize_database():

    connection = get_connection()

    # ---------------------------------------------------------
    # EPISODIC MEMORY
    # ---------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            goal TEXT NOT NULL,
            result TEXT,
            status TEXT NOT NULL
        )
        """
    )

    # ---------------------------------------------------------
    # SEMANTIC MEMORY
    # ---------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS semantic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_key TEXT UNIQUE NOT NULL,
            memory_value TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )

    # ---------------------------------------------------------
    # HUMAN INTERVENTION
    # ---------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS intervention_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT,
            task_id INTEGER NOT NULL,
            task_description TEXT NOT NULL,
            reason TEXT NOT NULL,
            category TEXT,
            status TEXT NOT NULL,
            response TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # ---------------------------------------------------------
    # EXECUTION MEMORY
    # ---------------------------------------------------------

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS execution_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id TEXT UNIQUE NOT NULL,
            goal TEXT NOT NULL,
            tasks TEXT NOT NULL,
            status TEXT NOT NULL,
            context TEXT,
            result TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # ---------------------------------------------------------
    # DATABASE MIGRATION
    # ---------------------------------------------------------

    # Existing databases created before execution_id was added
    # will be upgraded automatically.

    if not _column_exists(
        connection,
        "intervention_requests",
        "execution_id"
    ):

        connection.execute(
            """
            ALTER TABLE intervention_requests
            ADD COLUMN execution_id TEXT
            """
        )

    connection.commit()
    connection.close()