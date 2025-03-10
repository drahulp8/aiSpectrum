#!/usr/bin/env python
"""
Test script for the aiSpectrum summarizer module
"""

import unittest
from unittest.mock import patch, MagicMock
from routes.summarizer import ResponseSummarizer, summarize_responses
import os
from dotenv import load_dotenv

# Load environment variables (if any)
load_dotenv()

class TestSummarizer(unittest.TestCase):
    """Test cases for the ResponseSummarizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.environ.get("OPENAI_API_KEY", "mock_key")
        self.test_query = "What is the capital of France?"
        self.test_responses = {
            "model1": {
                "content": "The capital of France is Paris.",
                "model": "test-model-1",
                "status": "success"
            },
            "model2": {
                "content": "Paris is the capital city of France.",
                "model": "test-model-2",
                "status": "success"
            }
        }
    
    def test_format_responses(self):
        """Test the _format_responses_for_prompt method"""
        summarizer = ResponseSummarizer("mock_key")
        formatted = summarizer._format_responses_for_prompt(self.test_responses)
        
        # Check that both model names are in the formatted output
        self.assertIn("MODEL1", formatted)
        self.assertIn("MODEL2", formatted)
        
        # Check that content is in the formatted output
        self.assertIn("The capital of France is Paris.", formatted)
        self.assertIn("Paris is the capital city of France.", formatted)
        
        print("✅ _format_responses_for_prompt works correctly")
    
    def test_summarize_no_responses(self):
        """Test summarizing when no successful responses"""
        summarizer = ResponseSummarizer("mock_key")
        empty_responses = {
            "model1": {"status": "error", "content": "Error message"}
        }
        
        result = summarizer.summarize(self.test_query, empty_responses)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("No successful responses", result["content"])
        print("✅ summarize handles empty responses correctly")
    
    def test_summarize_one_response(self):
        """Test summarizing when only one successful response"""
        summarizer = ResponseSummarizer("mock_key")
        single_response = {
            "model1": {
                "content": "The capital of France is Paris.",
                "model": "test-model-1",
                "status": "success"
            }
        }
        
        result = summarizer.summarize(self.test_query, single_response)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("model1", result["content"])
        self.assertIn("The capital of France is Paris.", result["content"])
        print("✅ summarize handles single response correctly")
    
    @patch("openai.OpenAI")
    def test_summarize_with_openai(self, mock_openai):
        """Test summarizing with OpenAI client"""
        # Skip if no API key
        if self.api_key == "mock_key":
            print("⚠️ Skipping real OpenAI test (no API key provided)")
            return
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Paris is the capital of France."
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        summarizer = ResponseSummarizer(self.api_key)
        result = summarizer.summarize(self.test_query, self.test_responses)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "Paris is the capital of France.")
        print("✅ summarize with OpenAI works correctly")
    
    def test_summarize_responses_function(self):
        """Test the summarize_responses helper function"""
        with patch.object(ResponseSummarizer, 'summarize') as mock_summarize:
            mock_summarize.return_value = {
                "content": "Summary content",
                "model": "meta-summarizer",
                "status": "success"
            }
            
            result = summarize_responses(self.test_query, self.test_responses, self.api_key)
            
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["content"], "Summary content")
            print("✅ summarize_responses helper function works correctly")

def run_tests():
    """Run the test cases"""
    print("\n=== Testing Summarizer Module ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSummarizer)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run_tests()