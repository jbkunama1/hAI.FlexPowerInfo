import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import price_gateway

class PriceExportTests(unittest.TestCase):
    def setUp(self):
        self.token = 'dedicated-read-token-for-tests-only-123456789'
        self.env = patch.dict('os.environ', {'PRICE_READ_TOKEN': self.token})
        self.env.start()
        self.hosts = patch.object(price_gateway.legacy, 'allowed_hosts', ['*'])
        self.hosts.start()
        self.client = TestClient(price_gateway.app, base_url='http://localhost')

    def tearDown(self):
        self.hosts.stop()
        self.env.stop()

    def test_token_required_and_duplicates_rejected(self):
        self.assertEqual(self.client.get('/price.txt').status_code, 401)
        self.assertEqual(self.client.get('/price.txt?token=wrong').status_code, 401)
        self.assertEqual(self.client.get('/price.txt', params=[('token', self.token), ('token', self.token)]).status_code, 401)

    def test_number_only_and_no_cache(self):
        with patch.object(price_gateway, 'evaluate', return_value={'gross_ct': '-0.125'}):
            r = self.client.get('/price.txt', params={'token': self.token})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, '-0.125')
        self.assertIn('text/plain', r.headers['content-type'])
        self.assertEqual(r.headers['cache-control'], 'no-store')

    def test_missing_or_stale_returns_error_not_zero(self):
        with patch.object(price_gateway, 'evaluate', return_value=None):
            r = self.client.get('/price.txt', params={'token': self.token})
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.text, 'Unavailable')

    def test_disabled_and_separate_from_write_credentials(self):
        for token in ['', 'short', price_gateway.legacy.mcp_token, price_gateway.legacy.password]:
            with patch.dict('os.environ', {'PRICE_READ_TOKEN': token}):
                self.assertEqual(self.client.get('/price.txt', params={'token': token}).status_code, 401)

    def test_read_only(self):
        self.assertEqual(self.client.post('/price.txt', params={'token': self.token}).status_code, 405)
