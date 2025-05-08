from flask import Flask, request, jsonify
from spotlawful_ai.legal_analytics_service import LegalAnalyticsService, SubscriptionManager
from spotlawful_ai.legal_document_analysis import LegalDocumentAnalysis
from spotlawful_ai.parsing_syntax_grammar_ai import ParsingSyntaxGrammarAI
from spotlawful_ai.revenue_optimizer import RevenueOptimizer
import pandas as pd

app = Flask(__name__)

# Initialize components
ai_parser = ParsingSyntaxGrammarAI()
subscription_manager = SubscriptionManager()
legal_analytics_service = LegalAnalyticsService(ai_model=ai_parser, subscription_manager=subscription_manager)
legal_document_analysis = LegalDocumentAnalysis(ai_parser=ai_parser)

# Initialize Revenue Optimizer with sample data
sample_revenue_data = pd.DataFrame({
    'revenue': [100000, 120000, 130000, 125000, 140000]  # Example historical revenue data
})
revenue_optimizer = RevenueOptimizer(sample_revenue_data)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    subscription_manager.subscribe(user_id)
    return jsonify({'message': f'User {user_id} subscribed successfully.'})

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    subscription_manager.unsubscribe(user_id)
    return jsonify({'message': f'User {user_id} unsubscribed successfully.'})

@app.route('/legal-analytics', methods=['POST'])
def legal_analytics():
    user_id = request.json.get('user_id')
    legal_text = request.json.get('legal_text')
    if not user_id or not legal_text:
        return jsonify({'error': 'user_id and legal_text are required'}), 400
    try:
        insights = legal_analytics_service.provide_insights(user_id, legal_text)
        return jsonify({'insights': insights})
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403

@app.route('/document-analysis', methods=['POST'])
def document_analysis():
    document_text = request.json.get('document_text')
    if not document_text:
        return jsonify({'error': 'document_text is required'}), 400
    result = legal_document_analysis.analyze_document(document_text)
    return jsonify(result)

@app.route('/optimize-revenue', methods=['GET'])
def optimize_revenue():
    report = revenue_optimizer.generate_report()
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
