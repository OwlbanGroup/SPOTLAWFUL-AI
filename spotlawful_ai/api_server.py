
from flask import Flask, request, jsonify
from spotlawful_ai.enhanced_legal_ai import EnhancedLegalAI

app = Flask(__name__)

# Initialize enhanced legal AI
enhanced_legal_ai = EnhancedLegalAI()

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

if __name__ == '__main__':
    # Run with Waitress production server for LAN access
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
