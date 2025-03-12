#!/usr/bin/env python
"""
Test script for the aiSpectrum API endpoints
This will help diagnose issues with the AI model responses
"""

import requests
import json
import sys
import time
import os
from dotenv import load_dotenv


# Load environment variables (if any)
load_dotenv()

# Base URL for API
BASE_URL = "http://localhost:5000/api"

def test_models_endpoint():
    """Test the /api/models endpoint"""
    print("\n=== Testing /api/models endpoint ===")
    
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} models available")
            for provider, info in data.items():
                print(f"  - {info['name']} ({provider}): {len(info['models'])} model options")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_single_model(provider, api_key, model_id=None):
    """Test a single AI model with the provided API key"""
    print(f"\n=== Testing {provider} API ===")
    
    # Simple test query
    test_query = "What is the capital of France? Give a very brief answer."
    
    # Prepare API keys structure
    api_keys = {
        provider: {
            "key": api_key
        }
    }
    
    # Add model if specified
    if model_id:
        api_keys[provider]["model"] = model_id
        print(f"Using model: {model_id}")
    
    try:
        print(f"Sending test query: '{test_query}'")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/query",
            json={
                "query": test_query,
                "api_keys": api_keys,
                "summarize": False
            },
            timeout=30  # 30 second timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if provider in data:
                model_response = data[provider]
                if model_response.get("status") == "success":
                    print(f"✅ Success! Response received in {elapsed:.2f} seconds")
                    print(f"Response: {model_response.get('content')[:100]}...")
                    return True
                else:
                    print(f"❌ Model error: {model_response.get('content')}")
                    return False
            else:
                print(f"❌ No response data for {provider}")
                print(f"Response data: {data}")
                return False
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def validate_api_key(provider, api_key):
    """Test the API key validation endpoint"""
    print(f"\n=== Validating {provider} API key ===")
    
    try:
        response = requests.post(
            f"{BASE_URL}/validate-key",
            json={
                "provider": provider,
                "api_key": api_key
            },
            timeout=15  # 15 second timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                print(f"✅ API key is valid: {data.get('message')}")
                return True
            else:
                print(f"❌ API key is invalid: {data.get('message')}")
                return False
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Main function to run the tests"""
    # First test the models endpoint
    if not test_models_endpoint():
        print("❌ Failed to fetch models. Make sure the Flask app is running on port 5000.")
        sys.exit(1)
    
    # List of providers to test
    providers = ["openai", "anthropic", "deepseek", "mistral", "gemini"]
    
    for provider in providers:
        # Try to get API key from environment variables
        api_key = os.environ.get(f"{provider.upper()}_API_KEY")
        if not api_key:
            print(f"\n⚠️ No API key found for {provider}. Skipping test.")
            continue
        
        # Validate API key
        if validate_api_key(provider, api_key):
            # Test with the API key
            test_single_model(provider, api_key)
        else:
            print(f"⚠️ Skipping {provider} model test due to invalid API key")
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()