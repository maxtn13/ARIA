"""
ARIA File Indexer — SQLite-based file indexing with content search
"""
import os, sqlite3, hashlib, json, re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Callable

SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', '.cache', 'venv', '.venv',
    'env', 'dist', 'build', '.trash', '.Trash', 'Trash', '.local/share/Trash',
    'proc', 'sys', 'dev', 'run', '.npm', '.cargo', '.rustup',
}

TEXT_EXTS = {
    '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json',
    '.yaml', '.yml', '.csv', '.xml', '.log', '.sh', '.bat', '.ini',
    '.conf', '.env', '.rst', '.java', '.cpp', '.c', '.h', '.go',
    '.rs', '.rb', '.php', '.swift', '.kt', '.r', '.sql', '.toml',
}

DOC_EXTS = {'.pdf', '.doc', '.docx', '.odt', '.rtf', '.xls', '.xlsx', '.pptx', '.ods'}
IMG_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'}
VID_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
AUD_EXTS = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
ARC_EXTS = {'.zip', '.tar', '.gz', '.rar', '.7z', '.bz2'}

TAG_RULES = {
    "invoice":  ["invoice", "receipt", "payment", "billing", "tax", "invoice"],
    "report":   ["report", "summary", "analysis", "quarterly", "annual"],
    "resume":   ["resume", "cv", "curriculum", "vitae"],
    "code":     [".py", ".js", ".ts", ".java", ".cpp", ".go", ".rs", ".c"],
    "config":   [".yaml", ".yml", ".json", ".ini", ".conf", ".env", ".toml"],
    "document": [".md", ".txt", ".rst", ".doc", ".docx", ".pdf"],
    "data":     [".csv", ".xlsx", ".json", "dataset", "export", "data"],
    "budget":   ["budget", "expense", "finance", "cost", "spending"],
    "notes":    ["note", "notes", "todo", "task", "journal", "diary"],
    "photo":    [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "video":    [".mp4", ".mkv", ".avi", ".mov"],
    "music":    [".mp3", ".wav", ".flac", ".aac"],
    "archive":  [".zip", ".tar", ".gz", ".rar", ".7z"],
    "script":   [".sh", ".bat", ".ps1", ".bash"],
}


class FileIndexer:
    def __init__(self, db_path: str = None):
        from aria_config import config
        self.db_path = db_path or config.get("index_db_path")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._total = 0
        self._done = 0

    def _init_db(self):
        with self._conn() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                name_lower TEXT NOT NULL,
                extension TEXT,
                size INTEGER,
                md5 TEXT,
                content TEXT,
                indexed_at TEXT,
                modified_at TEXT,
                tags TEXT
            )''')
            c.execute('CREATE INDEX IF NOT EXISTS idx_name ON files(name_lower)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_ext ON files(extension)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_md5 ON files(md5)')
            c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
                USING fts5(path, name, content, tags, content=files, content_rowid=id)
            ''')

    def _conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def get_stats(self) -> Dict:
        with self._conn() as c:
            total = c.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            by_ext = c.execute(
                "SELECT extension, COUNT(*) as n FROM files GROUP BY extension ORDER BY n DESC LIMIT 10"
            ).fetchall()
        return {
            "total_files": total,
            "by_extension": [dict(r) for r in by_ext],
            "db_path": self.db_path,
        }

    def index_directory(self, root_path: str, progress_cb: Callable = None,
                        status_cb: Callable = None) -> int:
        """Index files. progress_cb(done, total), status_cb(msg)"""
        root = Path(root_path).expanduser()
        if not root.exists():
            return 0

        # Count files first
        if status_cb: status_cb("Counting files...")
        all_files = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if d not in SKIP_DIRS and not d.startswith('.')]
            for fn in filenames:
                all_files.append(os.path.join(dirpath, fn))

        total = len(all_files)
        done = 0

        if status_cb: status_cb(f"Indexing {total:,} files...")

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        batch = []
        fts_batch = []

        for filepath in all_files:
            try:
                p = Path(filepath)
                stat = os.stat(filepath)
                ext = p.suffix.lower()
                name = p.name
                modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                md5 = self._hash_file(filepath) if stat.st_size < 50 * 1024 * 1024 else None
                content = self._read_content(filepath, ext)
                tags = self._auto_tag(name, ext, content)

                batch.append((
                    filepath, name, name.lower(), ext, stat.st_size,
                    md5, content, datetime.now().isoformat(), modified, json.dumps(tags)
                ))
                fts_batch.append((filepath, name, content or '', ' '.join(tags)))

                done += 1
                if done % 200 == 0:
                    conn.executemany('''INSERT OR REPLACE INTO files
                        (path, name, name_lower, extension, size, md5, content,
                         indexed_at, modified_at, tags)
                        VALUES (?,?,?,?,?,?,?,?,?,?)''', batch)
                    conn.executemany('''INSERT OR REPLACE INTO files_fts
                        (path, name, content, tags) VALUES (?,?,?,?)''', fts_batch)
                    conn.commit()
                    batch.clear()
                    fts_batch.clear()
                    if progress_cb: progress_cb(done, total)
                    if status_cb: status_cb(f"Indexed {done:,} / {total:,} files...")

            except (PermissionError, OSError, FileNotFoundError):
                done += 1
                continue

        if batch:
            conn.executemany('''INSERT OR REPLACE INTO files
                (path, name, name_lower, extension, size, md5, content,
                 indexed_at, modified_at, tags)
                VALUES (?,?,?,?,?,?,?,?,?,?)''', batch)
            conn.executemany('''INSERT OR REPLACE INTO files_fts
                (path, name, content, tags) VALUES (?,?,?,?)''', fts_batch)
            conn.commit()

        conn.close()
        if progress_cb: progress_cb(total, total)
        if status_cb: status_cb(f"✅ Done! Indexed {total:,} files.")
        return total

    def name_search(self, query: str, limit: int = 15) -> List[Dict]:
        """Fast name-based search with fuzzy matching."""
        q = query.strip().lower()
        if not q:
            return []
        with self._conn() as c:
            # Exact name match first
            rows = c.execute('''
                SELECT path, name, extension, size, tags, modified_at
                FROM files WHERE name_lower LIKE ?
                ORDER BY
                    CASE WHEN name_lower = ? THEN 0
                         WHEN name_lower LIKE ? THEN 1
                         ELSE 2 END,
                    size DESC
                LIMIT ?
            ''', (f'%{q}%', q, f'{q}%', limit)).fetchall()
        return [self._fmt(r) for r in rows]

    def content_search(self, query: str, limit: int = 12) -> List[Dict]:
        """Full-text search across file content."""
        q = query.strip()
        if not q:
            return []
        # Clean query for FTS5
        safe_q = re.sub(r'[^\w\s]', ' ', q)
        try:
            with self._conn() as c:
                rows = c.execute('''
                    SELECT f.path, f.name, f.extension, f.size, f.tags, f.modified_at
                    FROM files_fts ft
                    JOIN files f ON f.path = ft.path
                    WHERE files_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                ''', (safe_q, limit)).fetchall()
            if rows:
                return [self._fmt(r) for r in rows]
        except Exception:
            pass
        # Fallback: LIKE search on content
        with self._conn() as c:
            rows = c.execute('''
                SELECT path, name, extension, size, tags, modified_at
                FROM files WHERE content LIKE ? OR tags LIKE ?
                LIMIT ?
            ''', (f'%{q}%', f'%{q}%', limit)).fetchall()
        return [self._fmt(r) for r in rows]

    def smart_search(self, query: str, limit: int = 12) -> List[Dict]:
        """Combined: name search + content search, deduplicated."""
        name_results = self.name_search(query, limit)
        content_results = self.content_search(query, limit)
        seen = {r['path'] for r in name_results}
        combined = name_results[:]
        for r in content_results:
            if r['path'] not in seen:
                combined.append(r)
                seen.add(r['path'])
        return combined[:limit]

    def find_duplicates(self, limit: int = 50) -> List[Dict]:
        with self._conn() as c:
            rows = c.execute('''
                SELECT md5, GROUP_CONCAT(path, '|||') as paths, COUNT(*) as cnt, SUM(size) as total_size
                FROM files WHERE md5 IS NOT NULL AND md5 != ''
                GROUP BY md5 HAVING cnt > 1
                ORDER BY total_size DESC LIMIT ?
            ''', (limit,)).fetchall()
        result = []
        for row in rows:
            paths = row['paths'].split('|||')
            wasted = row['total_size'] - (row['total_size'] // row['cnt'])
            result.append({
                "md5": row['md5'],
                "count": row['cnt'],
                "files": paths,
                "wasted_bytes": wasted,
                "wasted_mb": round(wasted / (1024 * 1024), 2),
            })
        return result

    def recent_files(self, limit: int = 8) -> List[Dict]:
        with self._conn() as c:
            rows = c.execute('''
                SELECT path, name, extension, size, tags, modified_at
                FROM files ORDER BY modified_at DESC LIMIT ?
            ''', (limit,)).fetchall()
        return [self._fmt(r) for r in rows]

    def _hash_file(self, filepath: str) -> Optional[str]:
        try:
            h = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def _read_content(self, filepath: str, ext: str, max_chars=2000) -> Optional[str]:
        if ext not in TEXT_EXTS:
            return None
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_chars)
        except Exception:
            return None

    def _auto_tag(self, name: str, ext: str, content: Optional[str]) -> List[str]:
        name_l = name.lower()
        body = (content or '').lower()
        tags = []
        for tag, kws in TAG_RULES.items():
            if any(kw in name_l or kw == ext or kw in body[:500] for kw in kws):
                tags.append(tag)
        return list(set(tags))

    def _fmt(self, row) -> Dict:
        tags = []
        try:
            tags = json.loads(row['tags'] or '[]')
        except Exception:
            pass
        size = row['size'] or 0
        if size < 1024: size_str = f"{size} B"
        elif size < 1048576: size_str = f"{size//1024} KB"
        else: size_str = f"{size//1048576} MB"
        path = row['path']
        return {
            "path": path,
            "name": row['name'],
            "extension": row['extension'] or '',
            "size": size_str,
            "tags": tags,
            "directory": str(Path(path).parent),
            "modified": row['modified_at'][:10] if row['modified_at'] else '',
        }
