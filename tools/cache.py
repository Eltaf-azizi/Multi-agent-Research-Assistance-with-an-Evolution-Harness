"""
CACHE.PY - SQLite caching for responses
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path

class ResponseCache:
    """Cache LLM responses in SQLite"""
    
    def __init__(self, db_path: str = "cache.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_table()
    
    def _create_table(self):
        """Create cache table if not exists"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()
    
    def get(self, query: str) -> str:
        """Get cached response"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        result = self.conn.execute(
            "SELECT response FROM cache WHERE query_hash = ?",
            (query_hash,)
        ).fetchone()
        
        if result:
            # Update access count
            self.conn.execute(
                "UPDATE cache SET access_count = access_count + 1 WHERE query_hash = ?",
                (query_hash,)
            )
            self.conn.commit()
            return result[0]
        
        return None
    
    def set(self, query: str, response: str):
        """Cache a response"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        self.conn.execute(
            "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?, ?)",
            (query_hash, query, response, datetime.now(), 1)
        )
        self.conn.commit()
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        stats = self.conn.execute("""
            SELECT 
                COUNT(*) as total_entries,
                SUM(access_count) as total_accesses
            FROM cache
        """).fetchone()
        
        return {
            'total_entries': stats[0],
            'total_accesses': stats[1] or 0,
            'db_size': Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
        }
    
    def clear(self):
        """Clear the cache"""
        self.conn.execute("DELETE FROM cache")
        self.conn.commit()