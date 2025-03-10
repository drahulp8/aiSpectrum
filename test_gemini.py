import requests
import json
import sys

def test_gemini_key(api_key):
    """Test a Gemini API key with different models to find which one works."""
    
    test_message = "Hello! This is a test message to validate the API key."
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.5-pro-preview",
        "gemini-1.0-pro-latest",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    for model in models:
        try:
            print(f"\nTesting model: {model}")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": test_message}]}],
                "generationConfig": {"maxOutputTokens": 10}
            }
            
            print(f"URL: {url}")
            response = requests.post(url, headers=headers, json=payload)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Model {model} works with this API key!")
                print(f"Response: {response.json()}")
                return model
            else:
                print(f"Error: {response.text}")
        
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    print("\n❌ None of the tested models worked with this API key.")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_gemini.py YOUR_API_KEY")
        sys.exit(1)
    
    api_key = sys.argv[1]
    working_model = test_gemini_key(api_key)
    
    if working_model:
        print(f"\nCONFIRMED: Model {working_model} works with this API key")
        print("\nUpdate your code to use this model in routes/api.py")
    else:
        print("\nNo working models found. Check your API key or try again later.")