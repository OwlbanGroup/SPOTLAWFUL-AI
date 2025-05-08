import unittest
import json
from api_server import app

class ApiServerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_subscribe_unsubscribe(self):
        response = self.app.post('/subscribe', json={'user_id': 'testuser'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('subscribed successfully', response.get_data(as_text=True))

        response = self.app.post('/unsubscribe', json={'user_id': 'testuser'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('unsubscribed successfully', response.get_data(as_text=True))

    def test_legal_analytics_without_subscription(self):
        response = self.app.post('/legal-analytics', json={'user_id': 'nosub', 'legal_text': 'Test legal text'})
        self.assertEqual(response.status_code, 403)
        self.assertIn('User does not have an active subscription', response.get_data(as_text=True))

    def test_legal_analytics_with_subscription(self):
        self.app.post('/subscribe', json={'user_id': 'subuser'})
        response = self.app.post('/legal-analytics', json={'user_id': 'subuser', 'legal_text': 'Test legal text'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('insights', data)

    def test_document_analysis(self):
        response = self.app.post('/document-analysis', json={'document_text': 'Sample legal document text.'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('parse_result', data)
        self.assertIn('compliance_issues', data)

    def test_optimize_revenue(self):
        response = self.app.get('/optimize-revenue')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('optimized_revenue', data)
        self.assertIn('details', data)

if __name__ == '__main__':
    unittest.main()
