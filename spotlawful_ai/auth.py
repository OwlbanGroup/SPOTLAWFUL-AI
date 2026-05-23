"""
Authentication module for SPOTLAWFUL-AI.
Provides JWT-based authentication and authorization.
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from flask import g, jsonify, request

from spotlawful_ai.config import Config

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Authentication error."""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class JWTManager:
    """JWT token management."""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or Config.JWT_SECRET_KEY
        self.algorithm = Config.JWT_ALGORITHM
        self.expiration_hours = Config.JWT_EXPIRATION_HOURS

    def _base64_encode(self, data: bytes) -> str:
        """URL-safe base64 encoding."""
        import base64
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    def _base64_decode(self, data: str) -> bytes:
        """URL-safe base64 decoding."""
        import base64
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)

    def _create_signature(self, header_payload: str) -> str:
        """Create HMAC signature."""
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            header_payload.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        return self._base64_encode(signature)

    def create_token(
        self,
        user_id: str,
        roles: Optional[List[str]] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a JWT token."""
        now = datetime.utcnow()

        # Header
        header = {
            "alg": self.algorithm,
            "typ": "JWT"
        }
        header_b64 = self._base64_encode(
            json.dumps(header, separators=(",", ":")).encode("utf-8")
        )

        # Payload
        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=self.expiration_hours)).timestamp()),
            "roles": roles or ["user"]
        }
        if custom_claims:
            payload.update(custom_claims)

        payload_b64 = self._base64_encode(
            json.dumps(payload, separators=(",", ":")).encode("utf-8")
        )

        # Signature
        signature = self._create_signature(f"{header_b64}.{payload_b64}")

        return f"{header_b64}.{payload_b64}.{signature}"

    def verify_token(self, jwt_token: str) -> Tuple[bool, Dict[str, Any]]:
        """Verify a JWT token and return payload if valid."""
        try:
            parts = jwt_token.split(".")
            if len(parts) != 3:
                return False, {"error": "Invalid token format"}

            header_b64, payload_b64, signature = parts

            expected_signature = self._create_signature(f"{header_b64}.{payload_b64}")
            if not hmac.compare_digest(signature, expected_signature):
                return False, {"error": "Invalid signature"}

            claims = json.loads(self._base64_decode(payload_b64).decode("utf-8"))

            exp = claims.get("exp", 0)
            if exp < time.time():
                return False, {"error": "Token expired"}

            return True, claims

        except (
            ValueError,
            TypeError,
            json.JSONDecodeError,
            UnicodeDecodeError,
        ) as err:
            logger.error("Token verification error: %s", err)
            return False, {"error": str(err)}

    def decode_token(self, jwt_token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging)."""
        parts = jwt_token.split(".")
        if len(parts) != 3:
            raise AuthError("Invalid token format")

        return json.loads(self._base64_decode(parts[1]).decode("utf-8"))


class AuthenticationMiddleware:
    """Flask middleware for JWT authentication, IP control, and audit logging."""

    def __init__(self, app: Optional[Any] = None) -> None:
        self.jwt_manager = JWTManager()
        self.app = app
        self.public_endpoints: Set[str] = {"/", "/health", "/docs"}
        self.public_api_endpoints = {
            "/subscribe",
            "/unsubscribe",
            "/feedback",
            "/deploy",
            "/optimize-revenue",
            "/training/advanced",
            "/assets/inventory",
            "/assets/inventory/decrypt",
            "/assets/backup",
            "/assets/backup/recover",
            "/assets/acl",
            "/auth/api-key",
            "/security/ip/allow",
            "/security/ip/block",
            "/security/ip/lists",
            "/legal-analytics",
            "/document-analysis",
            "/continuous-learning",
        }
        self.blocked_ips: Set[str] = set()
        self.allowed_ips: Set[str] = set()

    def init_app(self, app: Any) -> None:
        """Initialize with Flask app."""
        self.app = app
        app.before_request(self._check_ip_access)
        app.before_request(self._check_auth)
        app.after_request(self._audit_response)

    def _check_ip_access(self) -> Optional[Tuple[Any, int]]:
        """Check allowlist/blocklist IP policy."""
        client_ip = (
            request.headers.get("X-Forwarded-For", request.remote_addr or "")
            .split(",")[0]
            .strip()
        )
        if client_ip in self.blocked_ips:
            return jsonify({"error": "Access denied from this IP"}), 403
        if self.allowed_ips and client_ip not in self.allowed_ips:
            return jsonify({"error": "IP not allowlisted"}), 403
        return None

    def _check_auth(self) -> Optional[Tuple[Any, int]]:
        """Check authentication before request."""
        # Skip public endpoints
        if request.path in self.public_endpoints:
            return None

        # Skip public API endpoints (they have their own validation)
        if any(request.path.startswith(endpoint) for endpoint in self.public_api_endpoints):
            return None

        # Check for API key first
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if api_key:
            return self._validate_api_key(api_key)

        # Check for Bearer token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return self._validate_token(token)

        # No auth provided
        return jsonify({"error": "Authentication required"}), 401

    def _validate_api_key(self, api_key: str) -> Optional[Tuple[Any, int]]:
        """Validate API key."""
        from spotlawful_ai.database import db

        user_id = db.validate_api_key(api_key)
        if user_id:
            g.current_user = user_id
            g.auth_type = "api_key"
            return None

        return jsonify({"error": "Invalid API key"}), 401

    def _validate_token(self, jwt_token: str) -> Optional[Tuple[Any, int]]:
        """Validate JWT token."""
        token_valid, claims = self.jwt_manager.verify_token(jwt_token)

        if token_valid:
            g.current_user = claims.get("sub")
            g.user_roles = claims.get("roles", [])
            g.auth_type = "jwt"
            return None

        return jsonify({"error": claims.get("error", "Invalid token")}), 401

    def _audit_response(self, response: Any) -> Any:
        """Persist audit details for request/response cycle."""
        try:
            from spotlawful_ai.database import db

            user_id = getattr(g, "current_user", None)
            action = f"{request.method} {request.path}"
            db.add_audit_log(
                action=action,
                resource=request.path,
                user_id=user_id,
                method=request.method,
                path=request.path,
                ip_address=(
                    request.headers.get("X-Forwarded-For", request.remote_addr or "")
                    .split(",")[0]
                    .strip()
                ),
                status_code=response.status_code,
                metadata={
                    "auth_type": getattr(g, "auth_type", "none"),
                    "query_args": dict(request.args),
                },
            )
        except (
            ValueError,
            TypeError,
            AttributeError,
            json.JSONDecodeError,
        ) as err:
            logger.warning("Audit logging failed: %s", err)
        return response

    def require_roles(
        self, roles: List[str]
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to require specific roles."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_roles = getattr(g, "user_roles", [])
                if not any(role in user_roles for role in roles):
                    return jsonify({"error": "Insufficient permissions"}), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator


def generate_token(user_id: str, roles: Optional[List[str]] = None) -> str:
    """Generate a JWT token for a user."""
    jwt_manager = JWTManager()
    return jwt_manager.create_token(user_id, roles)


def verify_token(jwt_token: str) -> Tuple[bool, Dict[str, Any]]:
    """Verify a JWT token."""
    jwt_manager = JWTManager()
    return jwt_manager.verify_token(jwt_token)


# Rate limiting decorator
def rate_limit(requests: int = 100, window_seconds: int = 60):
    """Rate limiting decorator."""
    from spotlawful_ai.database import db

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            identifier = getattr(g, "current_user", request.remote_addr)

            if db.check_rate_limit(identifier, requests, window_seconds):
                return f(*args, **kwargs)

            return jsonify({
                "error": "Rate limit exceeded",
                "retry_after": window_seconds
            }), 429

        return decorated_function
    return decorator


# Example usage:
if __name__ == "__main__":
    DEMO_TOKEN = generate_token("user123", ["admin", "user"])
    print(f"Generated token: {DEMO_TOKEN[:50]}...")

    is_valid, demo_claims = verify_token(DEMO_TOKEN)
    print(f"Token valid: {is_valid}")
    print(f"Payload: {demo_claims}")
