# -*- coding: utf-8 -*-
"""SQLite correlation repository implementation."""

import json
import sqlite3
from typing import List, Optional
from datetime import datetime
from backend.agents.cross_evidence_correlation.repositories.base_repository import CorrelationRepository
from backend.agents.cross_evidence_correlation.schema import CorrelationCluster
from backend.agents.cross_evidence_correlation.exceptions import RepositoryError

class SQLiteRepository(CorrelationRepository):
    """Stores correlation clusters inside an SQLite database table."""
    
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        try:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS correlation_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    cluster_name TEXT,
                    primary_timestamp TEXT,
                    cluster_data TEXT
                )"""
            )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to initialize SQLite correlation database: {e}")

    def save_clusters(self, clusters: List[CorrelationCluster]) -> None:
        try:
            for c in clusters:
                ts_str = c.cluster_primary_timestamp.isoformat() if c.cluster_primary_timestamp else None
                self.conn.execute(
                    "INSERT OR REPLACE INTO correlation_clusters (cluster_id, cluster_name, primary_timestamp, cluster_data) VALUES (?, ?, ?, ?)",
                    (
                        c.cluster_id,
                        c.cluster_name,
                        ts_str,
                        c.model_dump_json()
                    )
                )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to save clusters to SQLite: {e}")

    def load_clusters(self) -> List[CorrelationCluster]:
        try:
            clusters = []
            cursor = self.conn.execute("SELECT cluster_data FROM correlation_clusters")
            for row in cursor.fetchall():
                clusters.append(CorrelationCluster.model_validate_json(row[0]))
            return clusters
        except Exception as e:
            raise RepositoryError(f"Failed to load clusters from SQLite: {e}")

    def clear_correlations(self) -> None:
        try:
            self.conn.execute("DELETE FROM correlation_clusters")
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to clear SQLite correlations: {e}")

    def get_cluster(self, cluster_id: str) -> Optional[CorrelationCluster]:
        try:
            cursor = self.conn.execute("SELECT cluster_data FROM correlation_clusters WHERE cluster_id = ?", (cluster_id,))
            row = cursor.fetchone()
            if row:
                return CorrelationCluster.model_validate_json(row[0])
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to fetch cluster {cluster_id} from SQLite: {e}")

    def list_clusters(self) -> List[CorrelationCluster]:
        return self.load_clusters()

    def find_by_entity(self, entity_id: str) -> List[CorrelationCluster]:
        return [c for c in self.load_clusters() if any(ent.entity_id == entity_id for ent in c.matched_entities)]

    def find_by_evidence(self, evidence_id: str) -> List[CorrelationCluster]:
        return [c for c in self.load_clusters() if evidence_id in c.matched_evidence]

    def find_by_time(self, start: datetime, end: datetime) -> List[CorrelationCluster]:
        res = []
        for c in self.load_clusters():
            if c.cluster_primary_timestamp and start <= c.cluster_primary_timestamp <= end:
                res.append(c)
        return res

    def find_by_graph_node(self, node_id: str) -> List[CorrelationCluster]:
        return [c for c in self.load_clusters() if node_id in c.graph_nodes]
export_sqlite_repository = SQLiteRepository
