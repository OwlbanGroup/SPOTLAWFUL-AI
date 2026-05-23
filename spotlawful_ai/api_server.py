"""
Spotlawful AI API Server.

This module provides a Flask-based REST API server for the Spotlawful AI system,
including endpoints for legal analytics, document analysis, AI agents, and
communication management.
"""

import base64
import hashlib
import json
from datetime import datetime

from flask import Flask, jsonify, request

from spotlawful_ai.auth import AuthenticationMiddleware, rate_limit
from spotlawful_ai.database import db

from spotlawful_ai.agent_protocol import AgentFeedback, AgentRequest
from spotlawful_ai.agents import DocumentAnalysisAgent, PredictionAgent, ResearchAgent
from spotlawful_ai.enhanced_legal_ai import EnhancedLegalAI
from spotlawful_ai.performance_monitoring import PerformanceMonitor
from spotlawful_ai.scalability_load_balancing import LoadBalancer
from spotlawful_ai.unified_communication_interface import UnifiedCommunicationInterface

app = Flask(__name__)
auth_middleware = AuthenticationMiddleware(app)
auth_middleware.init_app(app)

# Initialize enhanced legal AI
enhanced_legal_ai = EnhancedLegalAI()

# Initialize agent layer
document_analysis_agent = DocumentAnalysisAgent(ai_parser=enhanced_legal_ai.ai_parser)
prediction_agent = PredictionAgent(ai_model=enhanced_legal_ai.ai_parser)
research_agent = ResearchAgent()

# Initialize communication interface with example configs
email_config = {
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "username": "user@example.com",
    "password": "password",
}
sms_config = {
    "account_sid": "your_twilio_sid",
    "auth_token": "your_twilio_auth_token",
    "from_number": "+1234567890",
}
phone_config = {
    "account_sid": "your_twilio_sid",
    "auth_token": "your_twilio_auth_token",
    "from_number": "+1234567890",
}
social_config = {
    "platform": "twitter",
    "access_token": "your_twitter_bearer_token",
}

comm_interface = UnifiedCommunicationInterface(
    email_config, sms_config, phone_config, social_config
)
performance_monitor = PerformanceMonitor()
load_balancer = LoadBalancer(num_workers=4)


def _json_body() -> dict:
    """Extract and validate JSON body from request."""
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else {}


def _encrypt_payload(payload: dict) -> str:
    """Simple reversible payload obfuscation for protected asset storage."""
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    xored = bytes([b ^ 0x5A for b in raw])
    return base64.urlsafe_b64encode(xored).decode("utf-8")


def _decrypt_payload(ciphertext: str) -> dict:
    encoded = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))
    raw = bytes([b ^ 0x5A for b in encoded]).decode("utf-8")
    return json.loads(raw)


def _asset_fingerprint(asset_name: str, asset_type: str, owner_id: str) -> str:
    """Create deterministic fingerprint for asset identity."""
    key = f"{owner_id}:{asset_type}:{asset_name}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()


# API routes for subscription management
@app.route("/subscribe", methods=["POST"])
def subscribe():
    """Subscribe a user to the Spotlawful AI service."""
    user_id = _json_body().get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    enhanced_legal_ai.subscribe_user(user_id)
    return jsonify({"message": f"User {user_id} subscribed successfully."})


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    """Unsubscribe a user from the Spotlawful AI service."""
    user_id = _json_body().get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    enhanced_legal_ai.unsubscribe_user(user_id)
    return jsonify({"message": f"User {user_id} unsubscribed successfully."})


# API route for legal text analysis
@app.route("/legal-analytics", methods=["POST"])
@rate_limit(requests=60, window_seconds=60)
def legal_analytics():
    """Analyze legal text and provide insights."""
    body = _json_body()
    user_id = body.get("user_id")
    legal_text = body.get("legal_text")
    if not user_id or not legal_text:
        return jsonify({"error": "user_id and legal_text are required"}), 400
    try:
        insights = enhanced_legal_ai.analyze_legal_text(user_id, legal_text)
        return jsonify({"insights": insights})
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


# API route for document analysis
@app.route("/document-analysis", methods=["POST"])
@rate_limit(requests=60, window_seconds=60)
def document_analysis():
    """Analyze a legal document and return structured results."""
    document_text = _json_body().get("document_text")
    if not document_text:
        return jsonify({"error": "document_text is required"}), 400
    result = enhanced_legal_ai.analyze_document(document_text)
    return jsonify(result)


# Agent endpoints
@app.route("/agents/document-analysis", methods=["POST"])
def agent_document_analysis():
    """Handle document analysis requests via AI agent."""
    body = _json_body()
    request_obj = AgentRequest.from_payload(
        agent_name="document_analysis",
        payload={"document_text": body.get("document_text", "")},
        user_id=body.get("user_id"),
        metadata=body.get("metadata"),
        request_id=body.get("request_id"),
    )
    response = document_analysis_agent.handle(request_obj)
    return jsonify(response.__dict__), 200 if response.status == "success" else 400


@app.route("/agents/prediction", methods=["POST"])
def agent_prediction():
    """Handle prediction requests via AI agent."""
    body = _json_body()
    request_obj = AgentRequest.from_payload(
        agent_name="prediction",
        payload={
            "case_facts": body.get("case_facts", ""),
            "historical_data": body.get("historical_data", []),
        },
        user_id=body.get("user_id"),
        metadata=body.get("metadata"),
        request_id=body.get("request_id"),
    )
    response = prediction_agent.handle(request_obj)
    return jsonify(response.__dict__), 200 if response.status == "success" else 400


@app.route("/agents/research", methods=["POST"])
def agent_research():
    """Handle research requests via AI agent."""
    body = _json_body()
    request_obj = AgentRequest.from_payload(
        agent_name="research",
        payload={
            "research_topic": body.get("research_topic", ""),
            "jurisdiction": body.get("jurisdiction", "general"),
        },
        user_id=body.get("user_id"),
        metadata=body.get("metadata"),
        request_id=body.get("request_id"),
    )
    response = research_agent.handle(request_obj)
    return jsonify(response.__dict__), 200 if response.status == "success" else 400


@app.route("/agents/feedback", methods=["POST"])
def agent_feedback():
    """Record feedback for an AI agent's response."""
    body = _json_body()
    agent_name = body.get("agent_name")
    request_id = body.get("request_id")
    feedback_text = body.get("feedback")
    rating = body.get("rating")

    if not agent_name or not request_id or not feedback_text:
        return jsonify({
            "error": "agent_name, request_id, and feedback are required"
        }), 400

    feedback_obj = AgentFeedback(
        agent_name=agent_name,
        request_id=request_id,
        feedback=feedback_text,
        rating=rating,
        metadata=body.get("metadata", {})
    )

    agent_map = {
        "document_analysis": document_analysis_agent,
        "prediction": prediction_agent,
        "research": research_agent,
    }
    agent = agent_map.get(agent_name)
    if agent is None:
        return jsonify({"error": f"Unknown agent: {agent_name}"}), 404

    agent.record_feedback(feedback_obj)
    return jsonify(
        {
            "message": "Feedback recorded successfully.",
            "agent_name": agent_name,
            "feedback_count": agent.feedback_count(),
        }
    )


# API route for revenue optimization report
@app.route("/optimize-revenue", methods=["GET"])
@rate_limit(requests=30, window_seconds=60)
def optimize_revenue():
    """Generate and return a revenue optimization report."""
    report = enhanced_legal_ai.optimize_revenue()
    return jsonify(report)


# API route for collecting user feedback
@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """Collect general user feedback for the system."""
    user_feedback = _json_body().get("feedback")
    if not user_feedback:
        return jsonify({"error": "feedback is required"}), 400
    enhanced_legal_ai.collect_user_feedback(user_feedback)
    return jsonify({"message": "Feedback received. Thank you!"})


# API route for continuous learning update
@app.route("/continuous-learning", methods=["POST"])
@rate_limit(requests=20, window_seconds=60)
def continuous_learning():
    """Update the AI model with new legal cases for continuous learning."""
    new_cases = _json_body().get("new_legal_cases", [])
    enhanced_legal_ai.continuous_learning_update(new_cases)
    return jsonify({
        "message": f"Continuous learning updated with {len(new_cases)} new cases."
    })


# API route for deployment trigger (optional)
@app.route("/deploy", methods=["POST"])
@rate_limit(requests=10, window_seconds=60)
def deploy():
    """Trigger a deployment process for the AI system."""
    enhanced_legal_ai.deploy()
    return jsonify({"message": "Deployment process initiated."})


@app.route("/training/advanced", methods=["POST"])
@rate_limit(requests=20, window_seconds=60)
def advanced_training():
    """Phase 1: Advanced training module with OSCAR-BROOME-REVENUE data."""
    body = _json_body()
    user_id = body.get("user_id")
    training_data = body.get("training_data", [])
    dimensions = body.get("dimensions", ["universe", "dimensional"])
    if not user_id or not isinstance(training_data, list):
        return jsonify({"error": "user_id and training_data list are required"}), 400

    transformed = [
        {
            "source": item.get("source", "unknown"),
            "content": item.get("content", ""),
            "labels": item.get("labels", []),
            "dimension_scope": dimensions,
            "processed_at": datetime.utcnow().isoformat(),
        }
        for item in training_data
    ]
    return jsonify(
        {
            "message": "Advanced training data processed.",
            "user_id": user_id,
            "records_processed": len(transformed),
            "dimensions": dimensions,
        }
    )


@app.route("/assets/inventory", methods=["POST"])
@rate_limit(requests=40, window_seconds=60)
def create_or_update_asset():
    """Phase 3: Create/update asset inventory entry with encrypted payload."""
    body = _json_body()
    owner_id = body.get("owner_id")
    asset_name = body.get("asset_name")
    asset_type = body.get("asset_type")
    classification = body.get("classification", "standard")
    metadata = body.get("metadata", {})
    payload = body.get("payload", {})

    if not owner_id or not asset_name or not asset_type:
        return jsonify({"error": "owner_id, asset_name, and asset_type are required"}), 400

    encrypted_payload = _encrypt_payload(
        payload if isinstance(payload, dict) else {"raw": payload}
    )
    metadata = metadata if isinstance(metadata, dict) else {}
    metadata["fingerprint"] = _asset_fingerprint(asset_name, asset_type, owner_id)

    asset_id = db.upsert_asset(
        owner_id=owner_id,
        asset_name=asset_name,
        asset_type=asset_type,
        classification=classification,
        encrypted_payload=encrypted_payload,
        metadata=metadata,
    )
    return jsonify(
        {
            "message": "Asset stored.",
            "asset_id": asset_id,
            "classification": classification,
        }
    )


@app.route("/assets/inventory/decrypt", methods=["POST"])
@rate_limit(requests=20, window_seconds=60)
def decrypt_asset_payload():
    """Decrypt stored asset payload for authorized recovery workflows."""
    body = _json_body()
    encrypted_payload = body.get("encrypted_payload")
    if not encrypted_payload:
        return jsonify({"error": "encrypted_payload is required"}), 400
    try:
        decrypted = _decrypt_payload(encrypted_payload)
        return jsonify({"decrypted_payload": decrypted})
    except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
        return jsonify({"error": "Unable to decrypt payload"}), 400


@app.route("/auth/api-key", methods=["POST"])
@rate_limit(requests=20, window_seconds=60)
def issue_api_key():
    """Issue API key for a user for programmatic API access."""
    body = _json_body()
    user_id = body.get("user_id")
    name = body.get("name", "default")
    duration_days = body.get("duration_days", 365)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        duration_days = int(duration_days)
    except (TypeError, ValueError):
        return jsonify({"error": "duration_days must be an integer"}), 400

    db.create_user(user_id)
    api_key = db.create_api_key(user_id=user_id, name=name, duration_days=duration_days)
    return jsonify({"message": "API key issued.", "user_id": user_id, "api_key": api_key})


@app.route("/security/ip/allow", methods=["POST"])
@rate_limit(requests=15, window_seconds=60)
def allow_ip():
    """Add an IP to middleware allowlist."""
    body = _json_body()
    ip_address = body.get("ip_address")
    if not ip_address:
        return jsonify({"error": "ip_address is required"}), 400
    auth_middleware.allowed_ips.add(ip_address)
    auth_middleware.blocked_ips.discard(ip_address)
    return jsonify({"message": "IP allowlisted.", "ip_address": ip_address})


@app.route("/security/ip/block", methods=["POST"])
@rate_limit(requests=15, window_seconds=60)
def block_ip():
    """Add an IP to middleware blocklist."""
    body = _json_body()
    ip_address = body.get("ip_address")
    if not ip_address:
        return jsonify({"error": "ip_address is required"}), 400
    auth_middleware.blocked_ips.add(ip_address)
    auth_middleware.allowed_ips.discard(ip_address)
    return jsonify({"message": "IP blocklisted.", "ip_address": ip_address})


@app.route("/security/ip/lists", methods=["GET"])
@rate_limit(requests=30, window_seconds=60)
def ip_lists():
    """Retrieve current in-memory allowlist/blocklist."""
    return jsonify(
        {
            "allowed_ips": sorted(auth_middleware.allowed_ips),
            "blocked_ips": sorted(auth_middleware.blocked_ips),
        }
    )


@app.route("/assets/acl", methods=["POST"])
@rate_limit(requests=40, window_seconds=60)
def add_asset_acl():
    """Grant ACL permission to principal for an asset."""
    body = _json_body()
    asset_id = body.get("asset_id")
    principal_id = body.get("principal_id")
    permission = body.get("permission")

    if asset_id is None or not principal_id or not permission:
        return jsonify({"error": "asset_id, principal_id, and permission are required"}), 400

    try:
        asset_id = int(asset_id)
    except (TypeError, ValueError):
        return jsonify({"error": "asset_id must be an integer"}), 400

    asset = db.get_asset_by_id(asset_id)
    if not asset:
        return jsonify({"error": "asset not found"}), 404

    acl_id = db.add_asset_acl(asset_id=asset_id, principal_id=principal_id, permission=permission)
    return jsonify({"message": "ACL updated.", "acl_id": acl_id, "asset_id": asset_id})


@app.route("/assets/acl/<int:asset_id>", methods=["GET"])
@rate_limit(requests=40, window_seconds=60)
def list_asset_acl(asset_id: int):
    """List ACL permissions for an asset."""
    asset = db.get_asset_by_id(asset_id)
    if not asset:
        return jsonify({"error": "asset not found"}), 404

    entries = db.list_asset_acl(asset_id)
    return jsonify({"asset_id": asset_id, "entries": entries})


@app.route("/assets/backup", methods=["POST"])
@rate_limit(requests=30, window_seconds=60)
def create_asset_backup():
    """Create backup snapshot from current asset payload."""
    body = _json_body()
    asset_id = body.get("asset_id")
    if asset_id is None:
        return jsonify({"error": "asset_id is required"}), 400

    try:
        asset_id = int(asset_id)
    except (TypeError, ValueError):
        return jsonify({"error": "asset_id must be an integer"}), 400

    asset = db.get_asset_by_id(asset_id)
    if not asset:
        return jsonify({"error": "asset not found"}), 404

    snapshot_payload = asset.get("encrypted_payload")
    if not snapshot_payload:
        return jsonify({"error": "asset has no encrypted_payload to back up"}), 400

    backup_id = db.create_asset_backup(asset_id=asset_id, snapshot_payload=snapshot_payload)
    return jsonify({"message": "Backup created.", "backup_id": backup_id, "asset_id": asset_id})


@app.route("/assets/backup/<int:asset_id>", methods=["GET"])
@rate_limit(requests=30, window_seconds=60)
def list_asset_backups(asset_id: int):
    """List backups for an asset."""
    asset = db.get_asset_by_id(asset_id)
    if not asset:
        return jsonify({"error": "asset not found"}), 404

    backups = db.list_asset_backups(asset_id)
    return jsonify({"asset_id": asset_id, "backups": backups})


@app.route("/assets/backup/recover", methods=["POST"])
@rate_limit(requests=20, window_seconds=60)
def recover_asset_backup():
    """Recover asset payload from a backup snapshot."""
    body = _json_body()
    backup_id = body.get("backup_id")
    if backup_id is None:
        return jsonify({"error": "backup_id is required"}), 400

    try:
        backup_id = int(backup_id)
    except (TypeError, ValueError):
        return jsonify({"error": "backup_id must be an integer"}), 400

    asset_id = db.recover_asset_from_backup(backup_id)
    if asset_id is None:
        return jsonify({"error": "backup not found"}), 404

    return jsonify(
        {
            "message": "Asset recovered from backup.",
            "asset_id": asset_id,
            "backup_id": backup_id,
        }
    )


# Example function to handle incoming requests
def handle_request(user_id, message, subject=None, twiml_url=None):
    """Handle incoming requests by distributing via load balancer and sending messages.

    Args:
        user_id: The user identifier
        message: The message content
        subject: Optional subject line for email messages
        twiml_url: Optional TwiML URL for phone calls
    """
    # Distribute request via load balancer
    load_balancer.distribute_request(message)
    # Send message via preferred channels
    comm_interface.send_message(user_id, message, subject, twiml_url)
    # Record performance metrics (dummy values for example)
    performance_monitor.record_metric("latency", 0.5)
    performance_monitor.record_metric("accuracy", 0.9)
    performance_monitor.record_metric("error_rate", 0.01)
    performance_monitor.record_metric("user_satisfaction", 0.95)


if __name__ == "__main__":
    # Start monitoring and load balancer
    performance_monitor.start_monitoring(interval=60)
    load_balancer.start()
    # Run with Waitress production server for LAN access
    from waitress import serve  # type: ignore[import-untyped]

    serve(app, host="0.0.0.0", port=5000)
