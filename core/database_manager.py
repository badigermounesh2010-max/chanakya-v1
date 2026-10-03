import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = 'data/chanakya.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                locked INTEGER DEFAULT 0,
                offline INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity INTEGER,
                side TEXT,
                profit_loss REAL,
                status TEXT,
                created_at TEXT,
                closed_at TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS code_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                code TEXT,
                status TEXT,
                output TEXT,
                execution_time REAL,
                created_at TEXT
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT,
                created_at TEXT
            )
        ''')

        conn.commit()
        conn.close()
        logger.info('Database initialized')

    def add_trade(self, symbol: str, entry_price: float, quantity: int, side: str, status: str = 'open'):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO trades (symbol, entry_price, quantity, side, status, created_at) VALUES (?, ?, ?, ?, ?, datetime("now"))',
            (symbol, entry_price, quantity, side, status),
        )
        conn.commit()
        conn.close()

    def save_code(self, command: str, code: str, status: str = 'pending', output: str = '', exec_time: float = 0.0):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO code_history (command, code, status, output, execution_time, created_at) VALUES (?, ?, ?, ?, ?, datetime("now"))',
            (command, code, status, output, exec_time),
        )
        conn.commit()
        conn.close()

    def save_memory(self, key: str, value: Any):
        import sqlite3, json
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO memory (key, value, created_at) VALUES (?, ?, datetime("now"))',
            (key, json.dumps(value)),
        )
        conn.commit()
        conn.close()

    def get_memory(self, key: str):
        import sqlite3, json
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        row = cur.execute('SELECT value FROM memory WHERE key=? ORDER BY id DESC LIMIT 1', (key,)).fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None

    def get_trades(self, limit: int = 100):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        rows = cur.execute('SELECT * FROM trades ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        conn.close()
        return rows
