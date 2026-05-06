#!/usr/bin/env python3
"""
Storage manager - SQLite-based clipboard history storage.
"""

import sqlite3
import json
import os
import time
import hashlib
from typing import Optional, List, Dict, Any


class StorageManager:
    """SQLite-based storage for clipboard history with encryption support."""

    def __init__(self, db_path: str = None):
        """Initialize storage manager.

        Args:
            db_path: Path to SQLite database file. Defaults to ~/.clipvault/history.db
        """
        if db_path is None:
            config_dir = os.path.expanduser('~/.clipvault')
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, 'history.db')

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        """Initialize database tables."""
        conn = self._get_connection()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS clips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'text',
                    title TEXT DEFAULT '',
                    pinned INTEGER DEFAULT 0,
                    copy_count INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    meta TEXT DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_clips_hash ON clips(content_hash);
                CREATE INDEX IF NOT EXISTS idx_clips_category ON clips(category);
                CREATE INDEX IF NOT EXISTS idx_clips_pinned ON clips(pinned);
                CREATE INDEX IF NOT EXISTS idx_clips_created ON clips(created_at);

                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'text',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_copies INTEGER DEFAULT 0,
                    by_category TEXT DEFAULT '{}',
                    top_items TEXT DEFAULT '[]'
                );
            """)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA-256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def add_clip(self, content: str, category: str = 'text',
                 title: str = '', meta: Dict = None) -> Optional[int]:
        """Add a new clip to storage.

        Args:
            content: Clip content text
            category: Content category (text/code/link/path/image)
            title: Optional title
            meta: Optional metadata dict

        Returns:
            Clip ID or None if duplicate
        """
        content_hash = self._compute_hash(content)
        now = time.time()
        meta_json = json.dumps(meta or {}, ensure_ascii=False)

        conn = self._get_connection()
        try:
            # Check for duplicate
            existing = conn.execute(
                "SELECT id FROM clips WHERE content_hash = ? ORDER BY created_at DESC LIMIT 1",
                (content_hash,)
            ).fetchone()

            if existing:
                # Update timestamp for existing item
                conn.execute(
                    "UPDATE clips SET updated_at = ?, copy_count = copy_count + 1 WHERE id = ?",
                    (now, existing['id'])
                )
                conn.commit()
                return existing['id']

            # Insert new clip
            cursor = conn.execute(
                """INSERT INTO clips (content, content_hash, category, title, pinned, created_at, updated_at, meta)
                   VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
                (content, content_hash, category, title, now, now, meta_json)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_clip(self, clip_id: int) -> Optional[Dict]:
        """Get a clip by ID."""
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM clips WHERE id = ?", (clip_id,)).fetchone()
            if row:
                result = dict(row)
                result['meta'] = json.loads(result['meta'])
                return result
            return None
        finally:
            conn.close()

    def list_clips(self, limit: int = 20, offset: int = 0,
                   category: str = None, pinned_only: bool = False) -> List[Dict]:
        """List clips from storage."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM clips WHERE 1=1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)

            if pinned_only:
                query += " AND pinned = 1"

            query += " ORDER BY pinned DESC, updated_at DESC"

            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            rows = conn.execute(query, params).fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['meta'] = json.loads(result['meta'])
                results.append(result)
            return results
        finally:
            conn.close()

    def search_clips(self, query: str, limit: int = 20,
                     category: str = None) -> List[Dict]:
        """Search clips by content."""
        conn = self._get_connection()
        try:
            sql = "SELECT * FROM clips WHERE content LIKE ?"
            params = [f"%{query}%"]

            if category:
                sql += " AND category = ?"
                params.append(category)

            sql += " ORDER BY pinned DESC, updated_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sql, params).fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['meta'] = json.loads(result['meta'])
                results.append(result)
            return results
        finally:
            conn.close()

    def delete_clip(self, clip_id: int) -> bool:
        """Delete a clip by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def clear_all(self) -> int:
        """Clear all clips. Returns number of deleted items."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("DELETE FROM clips")
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def toggle_pin(self, clip_id: int) -> bool:
        """Toggle pin status of a clip."""
        conn = self._get_connection()
        try:
            clip = conn.execute("SELECT pinned FROM clips WHERE id = ?", (clip_id,)).fetchone()
            if not clip:
                return False
            new_pin = 0 if clip['pinned'] else 1
            conn.execute("UPDATE clips SET pinned = ? WHERE id = ?", (new_pin, clip_id))
            conn.commit()
            return True
        finally:
            conn.close()

    def increment_copy_count(self, clip_id: int):
        """Increment the copy count for a clip."""
        conn = self._get_connection()
        try:
            conn.execute(
                "UPDATE clips SET copy_count = copy_count + 1, updated_at = ? WHERE id = ?",
                (time.time(), clip_id)
            )
            conn.commit()
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get clipboard statistics."""
        conn = self._get_connection()
        try:
            total = conn.execute("SELECT COUNT(*) as cnt FROM clips").fetchone()['cnt']
            pinned = conn.execute("SELECT COUNT(*) as cnt FROM clips WHERE pinned = 1").fetchone()['cnt']

            category_stats = conn.execute("""
                SELECT category, COUNT(*) as cnt, SUM(copy_count) as total_copies
                FROM clips GROUP BY category ORDER BY cnt DESC
            """).fetchall()

            top_items = conn.execute("""
                SELECT id, title, category, copy_count
                FROM clips ORDER BY copy_count DESC LIMIT 10
            """).fetchall()

            recent = conn.execute("""
                SELECT COUNT(*) as cnt FROM clips
                WHERE created_at > ?
            """, (time.time() - 86400,)).fetchone()['cnt']

            return {
                'total': total,
                'pinned': pinned,
                'recent_24h': recent,
                'categories': [dict(r) for r in category_stats],
                'top_items': [dict(r) for r in top_items],
            }
        finally:
            conn.close()

    # Template methods
    def add_template(self, name: str, content: str, category: str = 'text') -> Optional[int]:
        """Add a template."""
        now = time.time()
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO templates (name, content, category, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, content, category, now, now)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_template(self, name: str) -> Optional[Dict]:
        """Get a template by name."""
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM templates WHERE name = ?", (name,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_templates(self) -> List[Dict]:
        """List all templates."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM templates ORDER BY updated_at DESC").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def delete_template(self, name: str) -> bool:
        """Delete a template by name."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("DELETE FROM templates WHERE name = ?", (name,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # Config methods
    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """Get a config value."""
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
            return row['value'] if row else default
        finally:
            conn.close()

    def set_config(self, key: str, value: str):
        """Set a config value."""
        conn = self._get_connection()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)""",
                (key, value, time.time())
            )
            conn.commit()
        finally:
            conn.close()

    def get_all_config(self) -> Dict[str, str]:
        """Get all config values."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT key, value FROM config").fetchall()
            return {r['key']: r['value'] for r in rows}
        finally:
            conn.close()

    def export_all(self) -> List[Dict]:
        """Export all clips for backup."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM clips ORDER BY created_at DESC").fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['meta'] = json.loads(result['meta'])
                results.append(result)
            return results
        finally:
            conn.close()

    def import_clips(self, clips: List[Dict]) -> int:
        """Import clips from backup. Returns number of imported items."""
        count = 0
        for clip in clips:
            content = clip.get('content', '')
            category = clip.get('category', 'text')
            title = clip.get('title', '')
            meta = clip.get('meta', {})
            result = self.add_clip(content, category, title, meta)
            if result:
                count += 1
        return count
