"""PostgreSQL connection pooling and transactional data access."""

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Any, Generator, Iterable, Sequence

import psycopg2
import psycopg2.extras
from psycopg2 import pool
from psycopg2.extensions import connection as PgConnection

from config import DatabaseConfig, load_database_config

TRIGGER_FRIENDLY_PATTERNS = (
    r"transaction rejected",
    r"completed and locked",
    r"trg_status_protection",
    r"status protection",
    r"bonus cannot be negative",
    r"not found in staff",
)


class DatabaseError(Exception):
    """User-facing database error with optional server detail."""

    def __init__(self, message: str, *, detail: str | None = None):
        super().__init__(message)
        self.detail = detail or message


class DatabaseManager:
    """Thread-safe connection pool wrapper for the lab database."""

    def __init__(self, config: DatabaseConfig | None = None):
        self.config = config or load_database_config()
        self._pool: pool.ThreadedConnectionPool | None = None
        self.schema = self.config.schema

    def initialize_pool(self) -> None:
        if self._pool is not None:
            return
        self._pool = pool.ThreadedConnectionPool(
            self.config.min_pool,
            self.config.max_pool,
            self.config.dsn,
        )

    def close_pool(self) -> None:
        if self._pool is not None:
            self._pool.closeall()
            self._pool = None

    @contextmanager
    def connection(self) -> Generator[PgConnection, None, None]:
        if self._pool is None:
            self.initialize_pool()
        assert self._pool is not None
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def cursor(self, *, dict_rows: bool = False) -> Generator[Any, None, None]:
        factory = psycopg2.extras.RealDictCursor if dict_rows else None
        with self.connection() as conn:
            cur = conn.cursor(cursor_factory=factory)
            try:
                yield cur
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

    def test_connection(self) -> tuple[bool, str]:
        try:
            with self.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    version = cur.fetchone()[0]
            self.detect_schema()
            return True, version
        except Exception as exc:
            return False, str(exc)

    def detect_schema(self) -> str:
        """Resolve labs vs public schema based on where lab_order lives."""
        query = """
            SELECT table_schema
            FROM information_schema.tables
            WHERE lower(table_name) = 'lab_order'
            ORDER BY CASE WHEN table_schema = %s THEN 0 ELSE 1 END
            LIMIT 1
        """
        with self.cursor() as cur:
            cur.execute(query, (self.config.schema,))
            row = cur.fetchone()
            if row:
                self.schema = row[0]
        return self.schema

    def qualify(self, table: str) -> str:
        return f'"{self.schema}"."{table}"'

    def execute(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
        *,
        fetch: str | None = None,
    ) -> list[Any] | Any | None:
        try:
            with self.cursor(dict_rows=True) as cur:
                cur.execute(sql, params)
                if fetch == "all":
                    return cur.fetchall()
                if fetch == "one":
                    return cur.fetchone()
                return None
        except psycopg2.Error as exc:
            raise self._wrap_error(exc) from exc

    def execute_many_notices(
        self, sql: str, params: Sequence[Any] | None = None
    ) -> list[str]:
        """Run SQL and collect PostgreSQL NOTICE messages (e.g. RAISE NOTICE)."""
        notices: list[str] = []
        try:
            with self.connection() as conn:
                conn.autocommit = False
                with conn.cursor() as cur:
                    cur.execute("SET client_min_messages TO NOTICE;")
                    cur.execute(sql, params)
                    notices = list(conn.notices)
                    conn.commit()
                conn.autocommit = True
        except psycopg2.Error as exc:
            raise self._wrap_error(exc) from exc
        return [self._clean_notice(n) for n in notices]

    def call_procedure(self, name: str, params: Sequence[Any] = ()) -> None:
        placeholders = ", ".join(["%s"] * len(params))
        sql = f"CALL {name}({placeholders})" if params else f"CALL {name}()"
        self.execute(sql, params if params else None)

    def fetch_doctor_workload(self, doctor_id: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        fn_candidates = [
            f"{self.schema}.fn_get_doctor_workload(%s)",
            "fn_get_doctor_workload(%s)",
        ]
        try:
            with self.connection() as conn:
                conn.autocommit = False
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    last_exc: psycopg2.Error | None = None
                    for fn_sql in fn_candidates:
                        try:
                            cur.execute(f"SELECT {fn_sql} AS cur_name", (doctor_id,))
                            last_exc = None
                            break
                        except psycopg2.Error as exc:
                            last_exc = exc
                            conn.rollback()
                    if last_exc is not None:
                        raise last_exc
                    result = cur.fetchone()
                    if not result or result["cur_name"] is None:
                        conn.commit()
                        return rows
                    cur.execute('FETCH ALL IN "doctor_cursor"')
                    rows = list(cur.fetchall())
                    conn.commit()
        except psycopg2.Error as exc:
            raise self._wrap_error(exc) from exc
        return rows

    def get_fk_options(self, sql: str) -> list[tuple[Any, str]]:
        rows = self.execute(sql, fetch="all") or []
        return [(r[list(r.keys())[0]], r[list(r.keys())[1]]) for r in rows]

    @staticmethod
    def _clean_notice(raw: str) -> str:
        return re.sub(r"^NOTICE:\s*", "", raw.strip(), flags=re.IGNORECASE)

    def _wrap_error(self, exc: psycopg2.Error) -> DatabaseError:
        raw = str(exc).strip()
        lower = raw.lower()
        for pattern in TRIGGER_FRIENDLY_PATTERNS:
            if re.search(pattern, lower):
                if "completed" in lower and "locked" in lower:
                    return DatabaseError(
                        "This laboratory order is COMPLETED and locked. "
                        "The server policy (trigger trg_status_protection) "
                        "rejected the modification.",
                        detail=raw,
                    )
                if "bonus cannot be negative" in lower:
                    return DatabaseError(
                        "Bonus amount cannot be negative.",
                        detail=raw,
                    )
                if "not found in staff" in lower:
                    return DatabaseError(
                        "The selected doctor was not found in the remote Staff system.",
                        detail=raw,
                    )
                return DatabaseError(
                    "The database rejected this transaction due to server policy.",
                    detail=raw,
                )
        return DatabaseError("Database operation failed.", detail=raw)


_db_singleton: DatabaseManager | None = None


def get_db() -> DatabaseManager:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = DatabaseManager()
    return _db_singleton
