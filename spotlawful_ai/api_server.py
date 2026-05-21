"""
Spotlawful AI API Server.

This module provides a Flask-based REST API server for the Spotlawful AI system,
including endpoints for legal analytics, document analysis, AI agents, and
communication management.
"""

from flask import Flask, request, jsonify

from spotlawful_ai.agent_protocol import AgentFeedback, AgentRequest
from spotlawful_ai.agents import DocumentAnalysisAgent, PredictionAgent, ResearchAgent
from spotlawful_ai.enhanced_legal_ai import EnhancedLegalAI
from spotlawful_ai.performance_monitoring import PerformanceMonitor
from spotlawful_ai.scalability_load_balancing import LoadBalancer
from spotlawful_ai.unified_communication_interface import UnifiedCommunicationInterface

app = Flask(__name__)

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
def continuous_learning():
    """Update the AI model with new legal cases for continuous learning."""
    new_cases = _json_body().get("new_legal_cases", [])
    enhanced_legal_ai.continuous_learning_update(new_cases)
    return jsonify({
        "message": f"Continuous learning updated with {len(new_cases)} new cases."
    })


# API route for deployment trigger (optional)
@app.route("/deploy", methods=["POST"])
def deploy():
    """Trigger a deployment process for the AI system."""
    enhanced_legal_ai.deploy()
    return jsonify({"message": "Deployment process initiated."})


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
