"""
Database module for SPOTLAWFUL-AI.
Provides SQLite persistence for subscriptions, feedback, and analytics.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
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

            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    method TEXT,
                    path TEXT,
                    ip_address TEXT,
                    status_code INTEGER,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # Asset inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_inventory (
                    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id TEXT NOT NULL,
                    asset_name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    classification TEXT DEFAULT 'standard',
                    encrypted_payload TEXT,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(owner_id, asset_name, asset_type)
                )
            """)

            # Access control list table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_acl (
                    acl_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    principal_id TEXT NOT NULL,
                    permission TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES asset_inventory(asset_id) ON DELETE CASCADE,
                    UNIQUE(asset_id, principal_id, permission)
                )
            """)

            # Backup snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_backups (
                    backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id INTEGER NOT NULL,
                    snapshot_payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES asset_inventory(asset_id) ON DELETE CASCADE
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
            logger.info("User %s subscribed to %s", user_id, plan_type)
            return True

    def unsubscribe_user(self, user_id: str) -> bool:
        """Unsubscribe a user."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subscriptions SET is_active = 0 WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            logger.info("User %s unsubscribed", user_id)
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
            logger.info("Feedback added: %s", cursor.lastrowid)
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
            logger.info("API key created for user %s", user_id)
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
        active_window_start = now - timedelta(seconds=window_seconds)

        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT request_count, window_start FROM rate_limits WHERE identifier = ?",
                (identifier,)
            )
            row = cursor.fetchone()

            if not row:
                cursor.execute(
                    (
                        "INSERT INTO rate_limits "
                        "(identifier, request_count, window_start) VALUES (?, ?, ?)"
                    ),
                    (identifier, 1, now.isoformat()),
                )
                return True

            stored_window_start = datetime.fromisoformat(row["window_start"])
            request_count = int(row["request_count"])

            if stored_window_start < active_window_start:
                cursor.execute(
                    (
                        "UPDATE rate_limits SET request_count = ?, window_start = ? "
                        "WHERE identifier = ?"
                    ),
                    (1, now.isoformat(), identifier),
                )
                return True

            if request_count >= limit:
                return False

            cursor.execute(
                "UPDATE rate_limits SET request_count = request_count + 1 WHERE identifier = ?",
                (identifier,)
            )
            return True


    # Audit logging
    def add_audit_log(
        self,
        action: str,
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        ip_address: Optional[str] = None,
        status_code: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Add an audit log entry for request/response activity."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO audit_logs
                (user_id, action, resource, method, path, ip_address, status_code, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    action,
                    resource,
                    method,
                    path,
                    ip_address,
                    status_code,
                    json.dumps(metadata or {}),
                    now,
                ),
            )
            return int(cursor.lastrowid)

    # Asset protection helpers
    def upsert_asset(
        self,
        owner_id: str,
        asset_name: str,
        asset_type: str,
        classification: str = "standard",
        encrypted_payload: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Create or update an asset inventory record and return its ID."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT asset_id FROM asset_inventory
                   WHERE owner_id = ? AND asset_name = ? AND asset_type = ?""",
                (owner_id, asset_name, asset_type),
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    """UPDATE asset_inventory
                       SET classification = ?, encrypted_payload = ?, metadata_json = ?, updated_at = ?
                       WHERE asset_id = ?""",
                    (
                        classification,
                        encrypted_payload,
                        json.dumps(metadata or {}),
                        now,
                        row["asset_id"],
                    ),
                )
                return int(row["asset_id"])

            cursor.execute(
                """INSERT INTO asset_inventory
                (owner_id, asset_name, asset_type, classification, encrypted_payload,
                 metadata_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    owner_id,
                    asset_name,
                    asset_type,
                    classification,
                    encrypted_payload,
                    json.dumps(metadata or {}),
                    now,
                    now,
                ),
            )
            return int(cursor.lastrowid)

    def get_asset_by_id(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """Fetch asset inventory row by ID."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM asset_inventory WHERE asset_id = ?",
                (asset_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_asset_acl(self, asset_id: int, principal_id: str, permission: str) -> int:
        """Create or ignore ACL permission for an asset principal."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                (
                    "INSERT OR IGNORE INTO asset_acl "
                    "(asset_id, principal_id, permission, created_at) "
                    "VALUES (?, ?, ?, ?)"
                ),
                (asset_id, principal_id, permission, now),
            )
            if cursor.lastrowid:
                return int(cursor.lastrowid)

            cursor.execute(
                """SELECT acl_id FROM asset_acl
                   WHERE asset_id = ? AND principal_id = ? AND permission = ?""",
                (asset_id, principal_id, permission),
            )
            existing = cursor.fetchone()
            return int(existing["acl_id"]) if existing else 0

    def list_asset_acl(self, asset_id: int) -> List[Dict[str, Any]]:
        """List ACL permissions for an asset."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT acl_id, asset_id, principal_id, permission, created_at
                   FROM asset_acl
                   WHERE asset_id = ?
                   ORDER BY created_at DESC""",
                (asset_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def create_asset_backup(self, asset_id: int, snapshot_payload: str) -> int:
        """Create a backup snapshot for an asset."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO asset_backups (asset_id, snapshot_payload, created_at)
                   VALUES (?, ?, ?)""",
                (asset_id, snapshot_payload, now),
            )
            return int(cursor.lastrowid)

    def list_asset_backups(self, asset_id: int) -> List[Dict[str, Any]]:
        """List backup snapshots for an asset."""
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT backup_id, asset_id, snapshot_payload, created_at
                   FROM asset_backups
                   WHERE asset_id = ?
                   ORDER BY created_at DESC""",
                (asset_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def recover_asset_from_backup(self, backup_id: int) -> Optional[int]:
        """Recover an asset encrypted payload using a backup snapshot."""
        now = datetime.utcnow().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT asset_id, snapshot_payload FROM asset_backups WHERE backup_id = ?",
                (backup_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute(
                """UPDATE asset_inventory
                   SET encrypted_payload = ?, updated_at = ?
                   WHERE asset_id = ?""",
                (row["snapshot_payload"], now, row["asset_id"]),
            )
            return int(row["asset_id"])


# Singleton database instance
db = Database()


def init_database() -> Database:
    """Initialize and return a fresh database instance."""
    return Database()


if __name__ == "__main__":
    # Test database operations
    logging.basicConfig(level=logging.INFO)
    demo_db = init_database()

    # Test user operations
    demo_db.create_user("test_user", "test@example.com")
    print("User created:", demo_db.get_user("test_user"))

    # Test subscription
    demo_db.subscribe_user("test_user", "premium", 30)
    print("Is subscribed:", demo_db.is_subscribed("test_user"))

    # Test feedback
    demo_db.add_feedback("test_user", "Great service!", 5)
    print("Feedback:", demo_db.get_feedback())

    # Test API key
    DEMO_KEY = demo_db.create_api_key("test_user", "test-key")
    print("API Key:", DEMO_KEY)
    print("Validated:", demo_db.validate_api_key(DEMO_KEY))
