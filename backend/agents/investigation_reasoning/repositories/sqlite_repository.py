# -*- coding: utf-8 -*-
"""SQLite reasoning repository implementation."""

import json
import sqlite3
from typing import List, Optional
from backend.agents.investigation_reasoning.repositories.base_repository import ReasoningRepository
from backend.agents.investigation_reasoning.schema import ReasoningPackage
from backend.agents.investigation_reasoning.exceptions import RepositoryError

class SQLiteRepository(ReasoningRepository):
    """Stores reasoning packages inside a local SQLite table."""
    
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        try:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS reasoning_packages (
                    reasoning_id TEXT PRIMARY KEY,
                    case_id TEXT,
                    retrieval_id TEXT,
                    package_data TEXT
                )"""
            )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to initialize SQLite reasoning database: {e}")

    def save_reasoning(self, package: ReasoningPackage) -> None:
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO reasoning_packages (reasoning_id, case_id, retrieval_id, package_data) VALUES (?, ?, ?, ?)",
                (package.reasoning_id, package.case_id, package.retrieval_id, package.model_dump_json())
            )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to save reasoning package: {e}")

    def load_reasoning(self, reasoning_id: str) -> Optional[ReasoningPackage]:
        try:
            cursor = self.conn.execute("SELECT package_data FROM reasoning_packages WHERE reasoning_id = ?", (reasoning_id,))
            row = cursor.fetchone()
            if row:
                return ReasoningPackage.model_validate_json(row[0])
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to load reasoning package: {e}")

    def list_reasonings(self) -> List[ReasoningPackage]:
        try:
            packages = []
            cursor = self.conn.execute("SELECT package_data FROM reasoning_packages")
            for row in cursor.fetchall():
                packages.append(ReasoningPackage.model_validate_json(row[0]))
            return packages
        except Exception as e:
            raise RepositoryError(f"Failed to list reasoning packages: {e}")

    def find_by_case(self, case_id: str) -> List[ReasoningPackage]:
        return [p for p in self.list_reasonings() if p.case_id == case_id]

    def find_by_retrieval(self, retrieval_id: str) -> List[ReasoningPackage]:
        return [p for p in self.list_reasonings() if p.retrieval_id == retrieval_id]

    def find_by_entity(self, entity_id: str) -> List[ReasoningPackage]:
        return [
            p for p in self.list_reasonings()
            if any(entity_id in f.supporting_entities for f in p.findings)
        ]

    def find_by_finding(self, finding_id: str) -> List[ReasoningPackage]:
        return [
            p for p in self.list_reasonings()
            if any(f.finding_id == finding_id for f in p.findings)
        ]

    def delete(self, reasoning_id: str) -> None:
        try:
            self.conn.execute("DELETE FROM reasoning_packages WHERE reasoning_id = ?", (reasoning_id,))
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to delete reasoning package: {e}")
export_sqlite_repository = SQLiteRepository
