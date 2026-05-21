"""
Database module for SPOTLAWFUL-AI.
Provides SQLite persistence for subscriptions, feedback, and analytics.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional
from spotlawful_ai.config import Config

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager with schema migrations."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_URL
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_schema(self):
        """Create tables if they don't exist."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    plan_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # User feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    feedback_text TEXT NOT NULL,
                    rating INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Legal analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS legal_analytics (
                    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # API keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    name TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    last_used_at TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Rate limiting table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    rate_limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT NOT NULL,
                    request_count INTEGER DEFAULT 0,
                    window_start TEXT NOT NULL,
                    UNIQUE(identifier)
                )
            """)
            
            logger.info("Database schema initialized")

    # User operations
    def create_user(self, user_id: str, email: Optional[str] = None) -> bool:
        """Create a new user."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR IGNORE INTO users (user_id, email, created_at, updated_at)
                   VALUES (?, ?, ?, ?)""",
                (user_id, email, now, now)
            )
            return cursor.rowcount > 0

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # Subscription operations
    def subscribe_user(
        self,
        user_id: str,
        plan_type: str = "standard",
        duration_days: Optional[int] = None
    ) -> bool:
        """Subscribe a user to a plan."""
        now = datetime.utcnow()
        start_date = now.isoformat()
        end_date = None
        if duration_days:
            end_date = (now + timedelta(days=duration_days)).isoformat()
        
        # Ensure user exists
        self.create_user(user_id)
        
        with self._transaction() as conn:
            cursor = conn.cursor()
            # Deactivate old subscriptions
            cursor.execute(
                "UPDATE subscriptions SET is_active = 0 WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            # Create new subscription
            cursor.execute(
                """INSERT INTO subscriptions (user_id, plan_type, start_date, end_date, is_active)
                   VALUES (?, ?, ?, ?, 1)""",
                (user_id, plan_type, start_date, end_date)
            )
            logger.info(f"User {user_id} subscribed to {plan_type}")
            return True

    def unsubscribe_user(self, user_id: str) -> bool:
        """Unsubscribe a user."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subscriptions SET is_active = 0 WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            logger.info(f"User {user_id} unsubscribed")
            return cursor.rowcount > 0

    def is_subscribed(self, user_id: str) -> bool:
        """Check if user has active subscription."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT is_active FROM subscriptions 
                   WHERE user_id = ? AND is_active = 1 
                   AND (end_date IS NULL OR end_date > ?)""",
                (user_id, datetime.utcnow().isoformat())
            )
            return cursor.fetchone() is not None

    # Feedback operations
    def add_feedback(
        self,
        user_id: Optional[str],
        feedback_text: str,
        rating: Optional[int] = None
    ) -> int:
        """Add user feedback."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO user_feedback (user_id, feedback_text, rating, created_at)
                   VALUES (?, ?, ?, ?)""",
                (user_id, feedback_text, rating, now)
            )
            logger.info(f"Feedback added: {cursor.lastrowid}")
            return cursor.lastrowid

    def get_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent feedback."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM user_feedback ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # Analytics operations
    def save_analytics(
        self,
        user_id: str,
        input_text: str,
        result: Dict[str, Any]
    ) -> int:
        """Save legal analytics result."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO legal_analytics (user_id, input_text, result_json, created_at)
                   VALUES (?, ?, ?, ?)""",
                (user_id, input_text, json.dumps(result), now)
            )
            return cursor.lastrowid

    # API Key operations
    def create_api_key(
        self,
        user_id: str,
        name: str = "default",
        duration_days: int = 365
    ) -> str:
        """Create an API key for a user."""
        import secrets
        api_key = f"slf_{secrets.token_urlsafe(32)}"
        now = datetime.utcnow()
        created_at = now.isoformat()
        expires_at = (now + timedelta(days=duration_days)).isoformat()
        
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO api_keys (user_id, api_key, name, created_at, expires_at, is_active)
                   VALUES (?, ?, ?, ?, ?, 1)""",
                (user_id, api_key, name, created_at, expires_at)
            )
            logger.info(f"API key created for user {user_id}")
            return api_key

    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return user_id if valid."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT user_id FROM api_keys 
                   WHERE api_key = ? AND is_active = 1 
                   AND (expires_at IS NULL OR expires_at > ?)""",
                (api_key, datetime.utcnow().isoformat())
            )
            row = cursor.fetchone()
            if row:
                # Update last used
                cursor.execute(
                    "UPDATE api_keys SET last_used_at = ? WHERE api_key = ?",
                    (datetime.utcnow().isoformat(), api_key)
                )
                return row["user_id"]
            return None

    # Rate limiting operations
    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Check if identifier is within rate limit."""
        now = datetime.utcnow()
        window_start = now.replace(second=now.second - window_seconds)
        
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT request_count FROM rate_limits 
                   WHERE identifier = ? AND window_start > ?""",
                (identifier, window_start.isoformat())
            )
            row = cursor.fetchone()
            
            if row and row["request_count"] >= limit:
                return False
            
            # Update or insert rate limit
            cursor.execute(
                """INSERT INTO rate_limits (identifier, request_count, window_start)
                   VALUES (?, 1, ?)
                   ON CONFLICT(identifier) DO UPDATE SET
                   request_count = request_count + 1""",
                (identifier, now.isoformat())
            )
            return True


# Singleton database instance
db = Database()


# Import timedelta for subscription calculations
from datetime import timedelta


def init_database():
    """Initialize database - call at application startup."""
    global db
    db = Database()
    logger.info("Database initialized")


if __name__ == "__main__":
    # Test database operations
    logging.basicConfig(level=logging.INFO)
    init_database()
    
    # Test user operations
    db.create_user("test_user", "test@example.com")
    print(f"User created: {db.get_user('test_user')}")
    
    # Test subscription
    db.subscribe_user("test_user", "premium", 30)
    print(f"Is subscribed: {db.is_subscribed('test_user')}")
    
    # Test feedback
    db.add_feedback("test_user", "Great service!", 5)
    print(f"Feedback: {db.get_feedback()}")
    
    # Test API key
    key = db.create_api_key("test_user", "test-key")
    print(f"API Key: {key}")
    print(f"Validated: {db.validate_api_key(key)}")
