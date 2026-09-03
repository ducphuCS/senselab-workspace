"""Private data access layer and SQLite repository for Library entities."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from backend.services.library.schemas import (
    EntityStatus,
    MethodCategory,
    OutputMetricsSchema,
    PrerequisitesSchema,
    PresetCreate,
    PresetRead,
    PresetUpdate,
    TestMethodCreate,
    TestMethodRead,
    TestMethodUpdate,
)

# Default data directory for Library service database
DEFAULT_DB_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "library.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts_str: str) -> datetime:
    return datetime.fromisoformat(ts_str)


class LibraryRepository:
    """SQLite repository for Library domain entities."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self._persistent_conn: sqlite3.Connection | None = None
        if db_path is None:
            DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
            self.db_path = str(DEFAULT_DB_PATH)
        elif str(db_path) == ":memory:":
            self.db_path = ":memory:"
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
            self._persistent_conn.execute("PRAGMA foreign_keys = ON;")
        else:
            if isinstance(db_path, Path):
                db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(db_path)
        self._init_tables()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        if self._persistent_conn is not None:
            with self._persistent_conn:
                yield self._persistent_conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            try:
                with conn:
                    yield conn
            finally:
                conn.close()

    def _init_tables(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_methods (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    procedure_json TEXT NOT NULL,
                    assumptions_json TEXT NOT NULL,
                    derived_from_id TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS presets (
                    id TEXT PRIMARY KEY,
                    test_method_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    prerequisites_json TEXT NOT NULL,
                    output_schema_json TEXT NOT NULL,
                    is_default INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'draft',
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (test_method_id) REFERENCES test_methods (id) ON DELETE CASCADE
                );
                """
            )
            conn.commit()

    # -----------------------------------------------------------------------
    # Helper serializers / deserializers
    # -----------------------------------------------------------------------

    def _row_to_preset_read(self, row: sqlite3.Row) -> PresetRead:
        prereqs_dict = json.loads(row["prerequisites_json"])
        output_dict = json.loads(row["output_schema_json"])
        return PresetRead(
            id=row["id"],
            test_method_id=row["test_method_id"],
            name=row["name"],
            description=row["description"],
            prerequisites=PrerequisitesSchema.model_validate(prereqs_dict),
            output_schema=OutputMetricsSchema.model_validate(output_dict),
            is_default=bool(row["is_default"]),
            status=row["status"],
            usage_count=row["usage_count"],
            created_at=_parse_iso(row["created_at"]),
            updated_at=_parse_iso(row["updated_at"]),
        )

    def _row_to_method_read(
        self, method_row: sqlite3.Row, preset_rows: list[sqlite3.Row]
    ) -> TestMethodRead:
        presets = [self._row_to_preset_read(r) for r in preset_rows]
        total_usage = sum(p.usage_count for p in presets)
        return TestMethodRead(
            id=method_row["id"],
            name=method_row["name"],
            category=method_row["category"],
            description=method_row["description"],
            procedure=json.loads(method_row["procedure_json"]),
            assumptions=json.loads(method_row["assumptions_json"]),
            derived_from_id=method_row["derived_from_id"],
            status=method_row["status"],
            presets=presets,
            total_usage_count=total_usage,
            created_at=_parse_iso(method_row["created_at"]),
            updated_at=_parse_iso(method_row["updated_at"]),
        )

    # -----------------------------------------------------------------------
    # Test Methods CRUD
    # -----------------------------------------------------------------------

    def create_test_method(self, data: TestMethodCreate) -> TestMethodRead:
        method_id = str(uuid.uuid4())
        now = _utc_now_iso()
        proc_json = json.dumps(data.procedure)
        assump_json = json.dumps(data.assumptions)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO test_methods (
                    id, name, category, description, procedure_json, assumptions_json,
                    derived_from_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, 'draft', ?, ?);
                """,
                (
                    method_id,
                    data.name,
                    data.category,
                    data.description,
                    proc_json,
                    assump_json,
                    now,
                    now,
                ),
            )

            # Insert initial presets if provided
            for idx, preset_data in enumerate(data.initial_presets):
                preset_id = str(uuid.uuid4())
                is_def = 1 if (preset_data.is_default or idx == 0) else 0
                conn.execute(
                    """
                    INSERT INTO presets (
                        id, test_method_id, name, description, prerequisites_json,
                        output_schema_json, is_default, status, usage_count, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', 0, ?, ?);
                    """,
                    (
                        preset_id,
                        method_id,
                        preset_data.name,
                        preset_data.description,
                        json.dumps(preset_data.prerequisites.model_dump()),
                        json.dumps(preset_data.output_schema.model_dump()),
                        is_def,
                        now,
                        now,
                    ),
                )

            conn.commit()

        return self.get_test_method(method_id)  # type: ignore[return-value]

    def get_test_method(self, method_id: str) -> TestMethodRead | None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test_methods WHERE id = ?;", (method_id,))
            method_row = cur.fetchone()
            if not method_row:
                return None

            cur.execute(
                "SELECT * FROM presets WHERE test_method_id = ? ORDER BY is_default DESC, created_at ASC;",
                (method_id,),
            )
            preset_rows = cur.fetchall()
            return self._row_to_method_read(method_row, preset_rows)

    def list_test_methods(
        self,
        category: MethodCategory | None = None,
        status: EntityStatus | None = None,
        search: str | None = None,
    ) -> list[TestMethodRead]:
        query = "SELECT * FROM test_methods WHERE 1=1"
        params: list[Any] = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if status:
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])

        query += " ORDER BY created_at DESC;"

        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            method_rows = cur.fetchall()

            results: list[TestMethodRead] = []
            for m_row in method_rows:
                cur.execute(
                    "SELECT * FROM presets WHERE test_method_id = ? ORDER BY is_default DESC, created_at ASC;",
                    (m_row["id"],),
                )
                preset_rows = cur.fetchall()
                results.append(self._row_to_method_read(m_row, preset_rows))

            return results

    def update_test_method(self, method_id: str, data: TestMethodUpdate) -> TestMethodRead:
        current = self.get_test_method(method_id)
        if not current:
            raise KeyError(f"Test method '{method_id}' not found.")

        # Guard: if in use, category cannot be changed
        if current.total_usage_count > 0 and data.category is not None and data.category != current.category:
            raise ValueError("Cannot change category of a test method that is currently in use.")

        updates: list[str] = []
        params: list[Any] = []

        if data.name is not None:
            updates.append("name = ?")
            params.append(data.name)
        if data.category is not None:
            updates.append("category = ?")
            params.append(data.category)
        if data.description is not None:
            updates.append("description = ?")
            params.append(data.description)
        if data.procedure is not None:
            updates.append("procedure_json = ?")
            params.append(json.dumps(data.procedure))
        if data.assumptions is not None:
            updates.append("assumptions_json = ?")
            params.append(json.dumps(data.assumptions))
        if data.status is not None:
            updates.append("status = ?")
            params.append(data.status)

        if updates:
            now = _utc_now_iso()
            updates.append("updated_at = ?")
            params.append(now)
            params.append(method_id)

            sql = f"UPDATE test_methods SET {', '.join(updates)} WHERE id = ?;"
            with self._connection() as conn:
                conn.execute(sql, params)
                conn.commit()

        return self.get_test_method(method_id)  # type: ignore[return-value]

    def delete_test_method(self, method_id: str) -> bool:
        current = self.get_test_method(method_id)
        if not current:
            raise KeyError(f"Test method '{method_id}' not found.")

        if current.total_usage_count > 0:
            raise ValueError("Cannot delete a test method that has historical test runs. Use archive instead.")

        with self._connection() as conn:
            conn.execute("DELETE FROM presets WHERE test_method_id = ?;", (method_id,))
            conn.execute("DELETE FROM test_methods WHERE id = ?;", (method_id,))
            conn.commit()

        return True

    def archive_test_method(self, method_id: str) -> TestMethodRead:
        current = self.get_test_method(method_id)
        if not current:
            raise KeyError(f"Test method '{method_id}' not found.")

        now = _utc_now_iso()
        with self._connection() as conn:
            conn.execute(
                "UPDATE test_methods SET status = 'archived', updated_at = ? WHERE id = ?;",
                (now, method_id),
            )
            conn.execute(
                "UPDATE presets SET status = 'archived', updated_at = ? WHERE test_method_id = ?;",
                (now, method_id),
            )
            conn.commit()

        return self.get_test_method(method_id)  # type: ignore[return-value]

    def duplicate_test_method(self, method_id: str, new_name: str | None = None) -> TestMethodRead:
        source = self.get_test_method(method_id)
        if not source:
            raise KeyError(f"Source test method '{method_id}' not found.")

        name_to_use = new_name or f"{source.name} (Copy)"
        new_method_id = str(uuid.uuid4())
        now = _utc_now_iso()

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO test_methods (
                    id, name, category, description, procedure_json, assumptions_json,
                    derived_from_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?);
                """,
                (
                    new_method_id,
                    name_to_use,
                    source.category,
                    source.description,
                    json.dumps(source.procedure),
                    json.dumps(source.assumptions),
                    source.id,
                    now,
                    now,
                ),
            )

            # Deep-copy all presets into new method as draft with 0 usage
            for p in source.presets:
                new_preset_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO presets (
                        id, test_method_id, name, description, prerequisites_json,
                        output_schema_json, is_default, status, usage_count, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', 0, ?, ?);
                    """,
                    (
                        new_preset_id,
                        new_method_id,
                        p.name,
                        p.description,
                        json.dumps(p.prerequisites.model_dump()),
                        json.dumps(p.output_schema.model_dump()),
                        1 if p.is_default else 0,
                        now,
                        now,
                    ),
                )

            conn.commit()

        return self.get_test_method(new_method_id)  # type: ignore[return-value]

    # -----------------------------------------------------------------------
    # Presets CRUD
    # -----------------------------------------------------------------------

    def create_preset(self, method_id: str, data: PresetCreate) -> PresetRead:
        method = self.get_test_method(method_id)
        if not method:
            raise KeyError(f"Parent test method '{method_id}' not found.")

        preset_id = str(uuid.uuid4())
        now = _utc_now_iso()

        # If method currently has 0 presets, this first one is automatically default
        is_default = 1 if (data.is_default or len(method.presets) == 0) else 0

        with self._connection() as conn:
            if is_default:
                # Demote other defaults
                conn.execute(
                    "UPDATE presets SET is_default = 0 WHERE test_method_id = ?;",
                    (method_id,),
                )

            conn.execute(
                """
                INSERT INTO presets (
                    id, test_method_id, name, description, prerequisites_json,
                    output_schema_json, is_default, status, usage_count, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'draft', 0, ?, ?);
                """,
                (
                    preset_id,
                    method_id,
                    data.name,
                    data.description,
                    json.dumps(data.prerequisites.model_dump()),
                    json.dumps(data.output_schema.model_dump()),
                    is_default,
                    now,
                    now,
                ),
            )
            conn.commit()

        return self.get_preset(preset_id)  # type: ignore[return-value]

    def get_preset(self, preset_id: str) -> PresetRead | None:
        with self._connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM presets WHERE id = ?;", (preset_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_preset_read(row)

    def update_preset(self, preset_id: str, data: PresetUpdate) -> PresetRead:
        current = self.get_preset(preset_id)
        if not current:
            raise KeyError(f"Preset '{preset_id}' not found.")

        if current.usage_count > 0:
            raise ValueError("Preset is in use by test runs and cannot be modified. Create a new preset instead.")

        updates: list[str] = []
        params: list[Any] = []

        if data.name is not None:
            updates.append("name = ?")
            params.append(data.name)
        if data.description is not None:
            updates.append("description = ?")
            params.append(data.description)
        if data.prerequisites is not None:
            updates.append("prerequisites_json = ?")
            params.append(json.dumps(data.prerequisites.model_dump()))
        if data.output_schema is not None:
            updates.append("output_schema_json = ?")
            params.append(json.dumps(data.output_schema.model_dump()))
        if data.is_default is not None:
            updates.append("is_default = ?")
            params.append(1 if data.is_default else 0)
        if data.status is not None:
            updates.append("status = ?")
            params.append(data.status)

        if updates:
            now = _utc_now_iso()
            updates.append("updated_at = ?")
            params.append(now)
            params.append(preset_id)

            sql = f"UPDATE presets SET {', '.join(updates)} WHERE id = ?;"
            with self._connection() as conn:
                if data.is_default:
                    conn.execute(
                        "UPDATE presets SET is_default = 0 WHERE test_method_id = ?;",
                        (current.test_method_id,),
                    )
                conn.execute(sql, params)
                conn.commit()

        return self.get_preset(preset_id)  # type: ignore[return-value]

    def delete_preset(self, preset_id: str) -> bool:
        current = self.get_preset(preset_id)
        if not current:
            raise KeyError(f"Preset '{preset_id}' not found.")

        if current.usage_count > 0:
            raise ValueError("Used presets cannot be deleted; archive them instead.")

        with self._connection() as conn:
            conn.execute("DELETE FROM presets WHERE id = ?;", (preset_id,))
            conn.commit()

        return True

    def archive_preset(self, preset_id: str) -> PresetRead:
        current = self.get_preset(preset_id)
        if not current:
            raise KeyError(f"Preset '{preset_id}' not found.")

        now = _utc_now_iso()
        with self._connection() as conn:
            conn.execute(
                "UPDATE presets SET status = 'archived', updated_at = ? WHERE id = ?;",
                (now, preset_id),
            )
            conn.commit()

        return self.get_preset(preset_id)  # type: ignore[return-value]

    def increment_preset_usage(self, preset_id: str) -> PresetRead:
        """Mark a preset as used in a Lab session, transitioning its state to active."""
        current = self.get_preset(preset_id)
        if not current:
            raise KeyError(f"Preset '{preset_id}' not found.")

        now = _utc_now_iso()
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE presets
                SET usage_count = usage_count + 1,
                    status = CASE WHEN status = 'draft' THEN 'active' ELSE status END,
                    updated_at = ?
                WHERE id = ?;
                """,
                (now, preset_id),
            )
            conn.execute(
                """
                UPDATE test_methods
                SET status = CASE WHEN status = 'draft' THEN 'active' ELSE status END,
                    updated_at = ?
                WHERE id = ?;
                """,
                (now, current.test_method_id),
            )
            conn.commit()

        return self.get_preset(preset_id)  # type: ignore[return-value]

    def close(self) -> None:
        """Close persistent connections if open."""
        if self._persistent_conn is not None:
            self._persistent_conn.close()
            self._persistent_conn = None


# Global singleton repository instance for the Library service
_default_repo: LibraryRepository | None = None


def set_library_repository(repo: LibraryRepository | None) -> None:
    """Set or reset the global repository instance (useful for test isolation)."""
    global _default_repo
    _default_repo = repo


def get_library_repository(db_path: str | Path | None = None) -> LibraryRepository:
    global _default_repo
    if db_path is not None:
        return LibraryRepository(db_path)
    if _default_repo is None:
        _default_repo = LibraryRepository()
    return _default_repo
