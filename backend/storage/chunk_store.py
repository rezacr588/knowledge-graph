"""
Persistent storage helper for ingested document chunks.

Stores chunk metadata as JSON to allow rehydrating indexes after a restart.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, List, Optional


class ChunkStore:
    """Simple JSON-backed store for chunk documents keyed by chunk id."""

    def __init__(self, path: str) -> None:
        self.path = path
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load_all(self) -> List[Dict]:
        """Load all stored chunks from disk."""
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                # Corrupted or partially written file; treat as empty.
                return []

        if not isinstance(payload, list):
            return []

        # Enforce consistent structure and de-duplicate by chunk id.
        dedup: Dict[str, Dict] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            chunk_id = item.get("id")
            if not chunk_id:
                continue
            dedup[str(chunk_id)] = item
        return list(dedup.values())

    def upsert(self, documents: Iterable[Dict]) -> List[Dict]:
        """
        Merge documents into the store, replacing any existing entries
        with the same chunk id.

        Returns the full list of stored documents.
        """
        existing = {doc["id"]: doc for doc in self.load_all() if "id" in doc}
        for doc in documents:
            doc_id = doc.get("id")
            if not doc_id:
                continue
            # Store a shallow copy to avoid mutating caller data.
            existing[str(doc_id)] = dict(doc)

        all_docs = list(existing.values())
        self._write(all_docs)
        return all_docs

    def clear(self) -> None:
        """Remove persisted chunks."""
        if os.path.exists(self.path):
            os.remove(self.path)

    def _write(self, documents: List[Dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(documents, handle, ensure_ascii=True, indent=2)
