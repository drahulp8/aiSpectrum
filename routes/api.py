from flask import Blueprint, request, jsonify, session
import anthropic
import openai
import requests
import json
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

# List of available AI models with their specs
AVAILABLE_MODELS = {
    'openai': {
        'name': 'OpenAI',
        'color': 'green',
        'icon': 'openai',
        'models': [
            {'id': 'gpt-4o', 'name': 'GPT-4o', 'description': 'Most capable model for complex tasks'},
            {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'Fast, capable large language model'},
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'Fast and cost-effective model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://platform.openai.com/account/api-keys',
        'docs_url': 'https://platform.openai.com/docs/guides/text-generation'
    },
    'anthropic': {
        'name': 'Anthropic',
        'color': 'purple',
        'icon': 'anthropic',
        'models': [
            {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus', 'description': 'Most powerful model for complex tasks'},
            {'id': 'claude-3-sonnet-20240229', 'name': 'Claude 3 Sonnet', 'description': 'Balanced performance and efficiency'},
            {'id': 'claude-3-haiku-20240307', 'name': 'Claude 3 Haiku', 'description': 'Fast and cost-effective model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://console.anthropic.com/keys',
        'docs_url': 'https://docs.anthropic.com/claude/docs'
    },
    'deepseek': {
        'name': 'DeepSeek',
        'color': 'blue',
        'icon': 'deepseek',
        'models': [
            {'id': 'deepseek-llm-67b-chat', 'name': 'DeepSeek Chat 67B', 'description': 'Large language model for chat'},
            {'id': 'deepseek-coder-33b-instruct', 'name': 'DeepSeek Coder 33B', 'description': 'Specialized for code generation'},
            {'id': 'deepseek-coder-6.7b-instruct', 'name': 'DeepSeek Coder 6.7B', 'description': 'Lightweight code generation model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://platform.deepseek.ai/',
        'docs_url': 'https://platform.deepseek.ai/docs'
    },
    'mistral': {
        'name': 'Mistral AI',
        'color': 'yellow',
        'icon': 'mistral',
        'models': [
            {'id': 'mistral-large-latest', 'name': 'Mistral Large', 'description': 'Most capable Mistral model'},
            {'id': 'mistral-medium-latest', 'name': 'Mistral Medium', 'description': 'Balanced performance model'},
            {'id': 'mistral-small-latest', 'name': 'Mistral Small', 'description': 'Fast, efficient Mistral model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://console.mistral.ai/api-keys/',
        'docs_url': 'https://docs.mistral.ai/'
    },
    'gemini': {
        'name': 'Google Gemini',
        'color': 'teal',
        'icon': 'google',
        'models': [
            {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': 'Most capable Google model'},
            {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'description': 'Fast, efficient Google model'},
            {'id': 'gemini-1.5-pro-preview', 'name': 'Gemini 1.5 Pro Preview', 'description': 'Preview of next-gen model'},
            {'id': 'gemini-1.0-pro-latest', 'name': 'Gemini 1.0 Pro', 'description': 'Previous generation model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://aistudio.google.com/app/apikey',
        'docs_url': 'https://ai.google.dev/docs'
    },
    'cohere': {
        'name': 'Cohere',
        'color': 'pink',
        'icon': 'cohere',
        'models': [
            {'id': 'command-r', 'name': 'Command R', 'description': 'Most powerful Cohere model'},
            {'id': 'command-r-plus', 'name': 'Command R+', 'description': 'Enhanced reasoning capabilities'},
            {'id': 'command-light', 'name': 'Command Light', 'description': 'Fast, lightweight model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://dashboard.cohere.com/api-keys',
        'docs_url': 'https://docs.cohere.com/'
    },
    'palm': {
        'name': 'Google PaLM',
        'color': 'lime',
        'icon': 'google',
        'models': [
            {'id': 'text-bison', 'name': 'Text Bison', 'description': 'Text generation model'},
            {'id': 'chat-bison', 'name': 'Chat Bison', 'description': 'Conversational model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://makersuite.google.com/app/apikey',
        'docs_url': 'https://developers.generativeai.google/guide/palm_api_overview'
    },
    'llama': {
        'name': 'Meta Llama',
        'color': 'indigo',
        'icon': 'meta',
        'models': [
            {'id': 'llama-3-70b-instruct', 'name': 'Llama 3 70B', 'description': 'Most capable Llama model'},
            {'id': 'llama-3-8b-instruct', 'name': 'Llama 3 8B', 'description': 'Efficient Llama model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://llama.meta.com/',
        'docs_url': 'https://llama.meta.com/docs/'
    },
    'azure': {
        'name': 'Azure OpenAI',
        'color': 'blue',
        'icon': 'microsoft',
        'models': [
            {'id': 'gpt-4', 'name': 'GPT-4', 'description': 'Most capable OpenAI model on Azure'},
            {'id': 'gpt-35-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'Fast and effective model'}
        ],
        'auth_type': 'api_key',
        'auth_url': 'https://portal.azure.com/',
        'docs_url': 'https://learn.microsoft.com/en-us/azure/ai-services/openai/'
    },
    'local': {
        'name': 'Local Models',
        'color': 'gray',
        'icon': 'server',
        'models': [
            {'id': 'localhost', 'name': 'Local Endpoint', 'description': 'Custom local model deployment'}
        ],
        'auth_type': 'none',
        'auth_url': '',
        'docs_url': 'https://localai.io/basics/'
    }
}

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Return list of available AI models"""
    return jsonify(AVAILABLE_MODELS)

from .summarizer import summarize_responses

@api_bp.route('/query', methods=['POST'])
def query_models():
    print("\n===== API QUERY REQUEST =====")
    data = request.json
    query = data.get('query')
    api_keys = data.get('api_keys', {})
    summarize = data.get('summarize', False)
    
    print(f"Query: {query}")
    print(f"API Keys provided for models: {list(api_keys.keys())}")
    print(f"Summarize enabled: {summarize}")
    
    results = {}
    
    # OpenAI
    if api_keys.get('openai'):
        print("Attempting OpenAI API call...")
        try:
            # Don't pass proxies parameter
            openai_client = openai.OpenAI(api_key=api_keys['openai']['key'])
            openai_model = api_keys['openai'].get('model', 'gpt-4o')
            print(f"Using OpenAI model: {openai_model}")
            
            print("Sending request to OpenAI API...")
            openai_response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ]
            )
            print("OpenAI API call successful!")
            
            results['openai'] = {
                'content': openai_response.choices[0].message.content,
                'model': openai_model,
                'status': 'success'
            }
            print(f"OpenAI response length: {len(openai_response.choices[0].message.content)} chars")
        except Exception as e:
            print(f"OpenAI API call failed with error: {str(e)}")
            results['openai'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }
    
    # Anthropic
    if api_keys.get('anthropic'):
        print("Attempting Anthropic API call...")
        try:
            # Direct API call for Anthropic instead of client
            api_key = api_keys['anthropic']['key']
            anthropic_model = api_keys['anthropic'].get('model', 'claude-3-opus-20240229')
            print(f"Using Anthropic model: {anthropic_model}")
            
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": anthropic_model,
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": query}
                ]
            }
            
            print("Sending request to Anthropic API...")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            print("Anthropic API call successful!")
            
            results['anthropic'] = {
                'content': response_data['content'][0]['text'],
                'model': anthropic_model,
                'status': 'success'
            }
            print(f"Anthropic response length: {len(response_data['content'][0]['text'])} chars")
        except Exception as e:
            print(f"Anthropic API call failed with error: {str(e)}")
            results['anthropic'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }
            
    # DeepSeek - using requests directly
    if api_keys.get('deepseek'):
        try:
            api_key = api_keys['deepseek']['key']
            deepseek_model = api_keys['deepseek'].get('model', 'deepseek-llm-67b-chat')
            
            # DeepSeek API endpoint (using deepseek.ai)
            url = "https://api.deepseek.ai/v1/chat/completions"
            
            # Request headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Request payload
            payload = {
                "model": deepseek_model,
                "messages": [
                    {"role": "user", "content": query}
                ]
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            response_data = response.json()
            
            results['deepseek'] = {
                'content': response_data['choices'][0]['message']['content'],
                'model': deepseek_model,
                'status': 'success'
            }
        except Exception as e:
            results['deepseek'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }
            
    # Mistral (if present)
    if api_keys.get('mistral'):
        try:
            api_key = api_keys['mistral']['key']
            mistral_model = api_keys['mistral'].get('model', 'mistral-large-latest')
            
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": mistral_model,
                "messages": [
                    {"role": "user", "content": query}
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            results['mistral'] = {
                'content': response_data['choices'][0]['message']['content'],
                'model': mistral_model,
                'status': 'success'
            }
        except Exception as e:
            results['mistral'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }

    # Google Gemini (if present)
    if api_keys.get('gemini'):
        print("Attempting Google Gemini API call...")
        try:
            api_key = api_keys['gemini']['key']
            
            # Try multiple models in case the selected one doesn't work
            gemini_models = [
                api_keys['gemini'].get('model', 'gemini-1.5-flash'),
                "gemini-1.5-flash",
                "gemini-pro",
                "gemini-pro-latest"
            ]
            
            # Remove duplicates while preserving order
            gemini_models = list(dict.fromkeys(gemini_models))
            
            success = False
            
            for gemini_model in gemini_models:
                try:
                    print(f"Trying Gemini model: {gemini_model}")
                    
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "contents": [
                            {"parts": [{"text": query}]}
                        ],
                        "generationConfig": {
                            "temperature": 0.7,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 2048
                        }
                    }
                    
                    print(f"Sending request to Gemini API with model {gemini_model}")
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    response_data = response.json()
                    print(f"Gemini API call successful with model {gemini_model}!")
                    
                    text_content = ""
                    if "candidates" in response_data and len(response_data["candidates"]) > 0:
                        parts = response_data["candidates"][0]["content"]["parts"]
                        for part in parts:
                            if "text" in part:
                                text_content += part["text"]
                    
                    results['gemini'] = {
                        'content': text_content,
                        'model': gemini_model,
                        'status': 'success'
                    }
                    print(f"Gemini response length: {len(text_content)} chars")
                    success = True
                    break
                    
                except Exception as model_error:
                    print(f"Failed with model {gemini_model}: {str(model_error)}")
                    continue
            
            if not success:
                raise Exception("All Gemini models failed to generate a response")
                
        except Exception as e:
            print(f"Gemini API call failed with error: {str(e)}")
            results['gemini'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }
    
    # Cohere (if present)
    if api_keys.get('cohere'):
        try:
            api_key = api_keys['cohere']['key']
            cohere_model = api_keys['cohere'].get('model', 'command-r')
            
            url = "https://api.cohere.ai/v1/chat"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": cohere_model,
                "message": query,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            results['cohere'] = {
                'content': response_data['text'],
                'model': cohere_model,
                'status': 'success'
            }
        except Exception as e:
            results['cohere'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }
            
    # Azure OpenAI (if present)
    if api_keys.get('azure'):
        try:
            api_key = api_keys['azure']['key']
            endpoint = api_keys['azure'].get('endpoint', '')
            azure_model = api_keys['azure'].get('model', 'gpt-4')
            deployment_name = api_keys['azure'].get('deployment', 'gpt4')
            
            url = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions?api-version=2023-05-15"
            headers = {
                "Content-Type": "application/json",
                "api-key": api_key
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            results['azure'] = {
                'content': response_data['choices'][0]['message']['content'],
                'model': azure_model,
                'status': 'success'
            }
        except Exception as e:
            results['azure'] = {
                'content': f"Error: {str(e)}",
                'status': 'error'
            }
    
    # Generate meta-summary if requested and if we have OpenAI or Gemini API key for summarization
    if summarize and (api_keys.get('openai') or api_keys.get('gemini')):
        print("Generating summary of responses...")
        summarizer_key = api_keys.get('openai', {}).get('key') or api_keys.get('gemini', {}).get('key')
        summary = summarize_responses(query, results, summarizer_key)
        results['summary'] = summary
        print(f"Summary status: {summary.get('status')}")
    
    print(f"Final results contain responses for: {list(results.keys())}")
    print("=== END OF API QUERY PROCESSING ===\n")
    
    return jsonify(results)

# Import the auth helper
from .auth import ApiAuth

# Endpoint to validate API keys
@api_bp.route('/validate-key', methods=['POST'])
def validate_key():
    """Validate an API key by making a simple request"""
    data = request.json
    provider = data.get('provider')
    api_key = data.get('api_key')
    
    # Use our auth helper to validate the key
    success, message = ApiAuth.validate_api_key(provider, api_key)
    
    return jsonify({
        'valid': success,
        'message': message
    })

@api_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Check if user is authenticated"""
    if session.get('user'):
        return jsonify({'authenticated': True, 'user': session['user']})
    else:
        return jsonify({'authenticated': False})

# Simple authentication using Flask sessions
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Login with email/password (mock)"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # In a real app, validate credentials; here we mock it
    if email and password:
        session['user'] = {
            'email': email,
            'name': email.split('@')[0],
            'id': '12345'
        }
        return jsonify({'success': True, 'user': session['user']})
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@api_bp.route('/auth/google', methods=['POST'])
def google_auth():
    """Mock Google OAuth"""
    data = request.json
    token = data.get('token')
    
    # In a real app, validate with Google; here we mock it
    if token:
        # Enhanced mock user data with more realistic profile info
        session['user'] = {
            'email': 'dev@techspectra.io',
            'name': 'Alex Chen',
            'id': 'google-12345',
            'picture': 'https://ui-avatars.com/api/?name=Alex+Chen&background=0D8ABC&color=fff',
            'given_name': 'Alex',
            'family_name': 'Chen',
            'locale': 'en',
            'verified_email': True
        }
        return jsonify({'success': True, 'user': session['user']})
    else:
        return jsonify({'success': False, 'error': 'Invalid token'}), 401

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user', None)
    return jsonify({'success': True})