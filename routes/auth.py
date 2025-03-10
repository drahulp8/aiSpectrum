import requests
import json

class ApiAuth:
    """
    Helper class for validating API keys for various AI providers
    """
    
    @staticmethod
    def validate_openai(api_key):
        """Validate OpenAI API key"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return True, "OpenAI API key is valid"
        except Exception as e:
            return False, f"API key validation failed: {str(e)}"
    
    @staticmethod
    def validate_anthropic(api_key):
        """Validate Anthropic API key"""
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}]
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return True, "Anthropic API key is valid"
        except Exception as e:
            return False, f"API key validation failed: {str(e)}"
    
    @staticmethod
    def validate_gemini(api_key):
        """Validate Google Gemini API key"""
        working_models = [
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-latest"
        ]
        
        for model in working_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": "Hello"}]}],
                    "generationConfig": {"maxOutputTokens": 10}
                }
                
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    return True, f"Google Gemini API key is valid (working model: {model})"
            except:
                continue
        
        return False, "API key validation failed: No working Gemini models found"
    
    @staticmethod
    def validate_mistral(api_key):
        """Validate Mistral API key"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return True, "Mistral API key is valid"
        except Exception as e:
            return False, f"API key validation failed: {str(e)}"
    
    @staticmethod
    def validate_api_key(provider, api_key):
        """
        Validate an API key for the specified provider
        
        Args:
            provider (str): The provider name (openai, anthropic, gemini, etc.)
            api_key (str): The API key to validate
            
        Returns:
            tuple: (success, message)
        """
        if not provider or not api_key:
            return False, "Provider and API key are required"
        
        validation_methods = {
            "openai": ApiAuth.validate_openai,
            "anthropic": ApiAuth.validate_anthropic,
            "gemini": ApiAuth.validate_gemini,
            "mistral": ApiAuth.validate_mistral
        }
        
        if provider in validation_methods:
            return validation_methods[provider](api_key)
        else:
            return False, f"Validation for {provider} not implemented"