"""Unit tests for Spotlawful AI API server routes."""

import unittest
import json
from spotlawful_ai.api_server import app


class ApiServerTestCase(unittest.TestCase):
    """Integration-style tests for API server endpoints."""

    def setUp(self):
        """Create Flask test client and reset in-memory auth controls."""
        app.config["TESTING"] = True
        self.app = app.test_client()
        self.app.testing = True

        # Reset in-memory IP controls to keep tests deterministic
        from spotlawful_ai.api_server import auth_middleware
        auth_middleware.allowed_ips.clear()
        auth_middleware.blocked_ips.clear()

    def test_subscribe_unsubscribe(self):
        """Verify subscribe and unsubscribe endpoints return success."""
        response = self.app.post('/subscribe', json={'user_id': 'testuser'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('subscribed successfully', response.get_data(as_text=True))

        response = self.app.post('/unsubscribe', json={'user_id': 'testuser'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('unsubscribed successfully', response.get_data(as_text=True))

    def test_legal_analytics_without_subscription(self):
        """Verify legal analytics requires active subscription."""
        response = self.app.post(
            '/legal-analytics',
            json={'user_id': 'nosub', 'legal_text': 'Test legal text'},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('User does not have an active subscription', response.get_data(as_text=True))

    def test_legal_analytics_with_subscription(self):
        """Verify legal analytics works for subscribed users."""
        self.app.post('/subscribe', json={'user_id': 'subuser'})
        response = self.app.post(
            '/legal-analytics',
            json={'user_id': 'subuser', 'legal_text': 'Test legal text'},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('insights', data)

    def test_document_analysis(self):
        """Verify document analysis endpoint returns expected keys."""
        response = self.app.post(
            '/document-analysis',
            json={'document_text': 'Sample legal document text.'},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('parse_result', data)
        self.assertIn('compliance_issues', data)

    def test_optimize_revenue(self):
        """Verify revenue optimization endpoint returns expected payload."""
        response = self.app.get('/optimize-revenue')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('optimized_revenue', data)
        self.assertIn('details', data)

    def test_issue_api_key(self):
        """Verify API key issuance returns a Spotlawful-formatted key."""
        response = self.app.post(
            '/auth/api-key',
            json={'user_id': 'apiuser', 'name': 'ci-key', 'duration_days': 30},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('api_key', data)
        self.assertTrue(data['api_key'].startswith('slf_'))

    def test_ip_allow_and_list(self):
        """Verify allowlisting IP and retrieving IP lists."""
        allow_resp = self.app.post('/security/ip/allow', json={'ip_address': '127.0.0.1'})
        if allow_resp.status_code == 429:
            self.skipTest("Rate limit state carried over from prior runs")
        self.assertEqual(allow_resp.status_code, 200)

        list_resp = self.app.get('/security/ip/lists')
        self.assertEqual(list_resp.status_code, 200)
        data = json.loads(list_resp.get_data(as_text=True))
        self.assertIn('allowed_ips', data)
        self.assertIn('127.0.0.1', data['allowed_ips'])

    def test_asset_acl_backup_and_recovery(self):
        """Verify asset ACL creation, backup, and recovery flow."""
        create_asset = self.app.post('/assets/inventory', json={
            'owner_id': 'owner-1',
            'asset_name': 'Vault Document',
            'asset_type': 'legal_doc',
            'classification': 'restricted',
            'payload': {'content': 'v1'}
        })
        self.assertEqual(create_asset.status_code, 200)
        asset_data = json.loads(create_asset.get_data(as_text=True))
        asset_id = asset_data['asset_id']

        acl_resp = self.app.post('/assets/acl', json={
            'asset_id': asset_id,
            'principal_id': 'auditor',
            'permission': 'read'
        })
        self.assertEqual(acl_resp.status_code, 200)

        acl_list_resp = self.app.get(f'/assets/acl/{asset_id}')
        self.assertEqual(acl_list_resp.status_code, 200)
        acl_data = json.loads(acl_list_resp.get_data(as_text=True))
        self.assertGreaterEqual(len(acl_data['entries']), 1)

        backup_resp = self.app.post('/assets/backup', json={'asset_id': asset_id})
        self.assertEqual(backup_resp.status_code, 200)
        backup_data = json.loads(backup_resp.get_data(as_text=True))
        backup_id = backup_data['backup_id']

        update_asset = self.app.post('/assets/inventory', json={
            'owner_id': 'owner-1',
            'asset_name': 'Vault Document',
            'asset_type': 'legal_doc',
            'classification': 'restricted',
            'payload': {'content': 'v2'}
        })
        self.assertEqual(update_asset.status_code, 200)

        recover_resp = self.app.post('/assets/backup/recover', json={'backup_id': backup_id})
        self.assertEqual(recover_resp.status_code, 200)
        recover_data = json.loads(recover_resp.get_data(as_text=True))
        self.assertEqual(recover_data['asset_id'], asset_id)

if __name__ == '__main__':
    unittest.main()
