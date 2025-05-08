from flask import Flask, request, jsonify
from spotlawful_ai.enhanced_legal_ai import EnhancedLegalAI
from spotlawful_ai.unified_communication_interface import UnifiedCommunicationInterface
from spotlawful_ai.performance_monitoring import PerformanceMonitor
from spotlawful_ai.scalability_load_balancing import LoadBalancer

app = Flask(__name__)

# Initialize enhanced legal AI
enhanced_legal_ai = EnhancedLegalAI()

# Initialize communication interface with example configs
email_config = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'username': 'user@example.com',
    'password': 'password'
}
sms_config = {
    'account_sid': 'your_twilio_sid',
    'auth_token': 'your_twilio_auth_token',
    'from_number': '+1234567890'
}
phone_config = {
    'account_sid': 'your_twilio_sid',
    'auth_token': 'your_twilio_auth_token',
    'from_number': '+1234567890'
}
social_config = {
    'platform': 'twitter',
    'access_token': 'your_twitter_bearer_token'
}

comm_interface = UnifiedCommunicationInterface(email_config, sms_config, phone_config, social_config)
performance_monitor = PerformanceMonitor()
load_balancer = LoadBalancer(num_workers=4)

# API routes for subscription management
@app.route('/subscribe', methods=['POST'])
def subscribe():
    print("Subscribe route called")
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    enhanced_legal_ai.subscribe_user(user_id)
    return jsonify({'message': f'User {user_id} subscribed successfully.'})
        
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    print("Unsubscribe route called")
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    enhanced_legal_ai.unsubscribe_user(user_id)
    return jsonify({'message': f'User {user_id} unsubscribed successfully.'})
        
# API route for legal text analysis
@app.route('/legal-analytics', methods=['POST'])
def legal_analytics():
    user_id = request.json.get('user_id')
    legal_text = request.json.get('legal_text')
    if not user_id or not legal_text:
        return jsonify({'error': 'user_id and legal_text are required'}), 400
    try:
        insights = enhanced_legal_ai.analyze_legal_text(user_id, legal_text)
        return jsonify({'insights': insights})
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403

# API route for document analysis
@app.route('/document-analysis', methods=['POST'])
def document_analysis():
    document_text = request.json.get('document_text')
    if not document_text:
        return jsonify({'error': 'document_text is required'}), 400
    result = enhanced_legal_ai.analyze_document(document_text)
    return jsonify(result)

# API route for revenue optimization report
@app.route('/optimize-revenue', methods=['GET'])
def optimize_revenue():
    report = enhanced_legal_ai.optimize_revenue()
    return jsonify(report)

# API route for collecting user feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_text = request.json.get('feedback')
    enhanced_legal_ai.collect_user_feedback(feedback_text)
    return jsonify({'message': 'Feedback received. Thank you!'})

# API route for continuous learning update
@app.route('/continuous-learning', methods=['POST'])
def continuous_learning():
    new_cases = request.json.get('new_legal_cases', [])
    enhanced_legal_ai.continuous_learning_update(new_cases)
    return jsonify({'message': f'Continuous learning updated with {len(new_cases)} new cases.'})

# API route for deployment trigger (optional)
@app.route('/deploy', methods=['POST'])
def deploy():
    enhanced_legal_ai.deploy()
    return jsonify({'message': 'Deployment process initiated.'})

# Example function to handle incoming requests
def handle_request(user_id, message, subject=None, twiml_url=None):
    # Distribute request via load balancer
    load_balancer.distribute_request(message)
    # Send message via preferred channels
    comm_interface.send_message(user_id, message, subject, twiml_url)
    # Record performance metrics (dummy values for example)
    performance_monitor.record_metric('latency', 0.5)
    performance_monitor.record_metric('accuracy', 0.9)
    performance_monitor.record_metric('error_rate', 0.01)
    performance_monitor.record_metric('user_satisfaction', 0.95)

if __name__ == '__main__':
    # Start monitoring and load balancer
    performance_monitor.start_monitoring(interval=60)
    load_balancer.start()
    # Run with Waitress production server for LAN access
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
