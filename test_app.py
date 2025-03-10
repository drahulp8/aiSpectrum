#!/usr/bin/env python
"""
Test script for the aiSpectrum Flask application
"""

import unittest
import json
import os
from app import app
from dotenv import load_dotenv

# Load environment variables (if any)
load_dotenv()

class TestApp(unittest.TestCase):
    """Test cases for the Flask application routes"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Create a test client
        self.client = app.test_client()
        
        # Test data
        self.test_query = "What is the capital of France?"
        
        # Get API keys from environment if available
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    def test_index_route(self):
        """Test the index route returns successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✅ Index route works correctly")
    
    def test_login_route(self):
        """Test the login route returns successfully"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        print("✅ Login route works correctly")
    
    def test_api_models_route(self):
        """Test the API models route returns available models"""
        response = self.client.get('/api/models')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('openai', data)
        self.assertIn('anthropic', data)
        print("✅ API models route works correctly")
    
    def test_api_auth_status_route(self):
        """Test the API auth status route"""
        response = self.client.get('/api/auth/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('authenticated', data)
        print("✅ API auth status route works correctly")
    
    def test_api_query_no_keys(self):
        """Test the API query route with no API keys"""
        payload = {
            "query": self.test_query,
            "api_keys": {},
            "summarize": False
        }
        
        response = self.client.post(
            '/api/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, {})  # Empty response with no API keys
        print("✅ API query route handles no keys correctly")
    
    def test_api_validate_key_missing_data(self):
        """Test the API validate key route with missing data"""
        payload = {}
        
        response = self.client.post(
            '/api/validate-key',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data.get('valid'))
        print("✅ API validate key route handles missing data correctly")

    @unittest.skipIf(not os.environ.get("OPENAI_API_KEY"), "Skipping OpenAI test (no API key)")
    def test_api_validate_openai_key(self):
        """Test OpenAI API key validation"""
        payload = {
            "provider": "openai",
            "api_key": self.openai_key
        }
        
        response = self.client.post(
            '/api/validate-key',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('valid'))
        print("✅ OpenAI API key validation works correctly")
    
    @unittest.skipIf(not os.environ.get("ANTHROPIC_API_KEY"), "Skipping Anthropic test (no API key)")
    def test_api_validate_anthropic_key(self):
        """Test Anthropic API key validation"""
        payload = {
            "provider": "anthropic",
            "api_key": self.anthropic_key
        }
        
        response = self.client.post(
            '/api/validate-key',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('valid'))
        print("✅ Anthropic API key validation works correctly")

def run_tests():
    """Run the test cases"""
    print("\n=== Testing Flask App Routes ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestApp)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run_tests()