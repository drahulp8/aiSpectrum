from flask import Blueprint, request, jsonify, session
import anthropic
import openai
import requests
import json
import os
import time
import uuid
import logging

# Set up logging
logger = logging.getLogger('aiSpectrum')

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

from .summarizer import summarize_responses, ResponseSummarizer

from .error_handler import handle_api_error, api_error_handler

@api_bp.route('/query', methods=['POST'])
@api_error_handler
def query_models():
    logger.info("\n===== API QUERY REQUEST =====")
    data = request.json
    query = data.get('query')
    api_keys = data.get('api_keys', {})
    summarize = data.get('summarize', False)
    
    logger.info(f"Query: {query}")
    logger.info(f"API Keys provided for models: {list(api_keys.keys())}")
    logger.info(f"Summarize enabled: {summarize}")
    
    results = {}
    
    # OpenAI
    if api_keys.get('openai'):
        logger.info("Attempting OpenAI API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
            # Don't pass proxies parameter
            openai_client = openai.OpenAI(api_key=api_keys['openai']['key'])
            openai_model = api_keys['openai'].get('model', 'gpt-4o')
            logger.info(f"Using OpenAI model: {openai_model}")
            
            logger.info("Sending request to OpenAI API...")
            openai_response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query}
                ]
            )
            logger.info("OpenAI API call successful!")
            
            results['openai'] = {
                'content': openai_response.choices[0].message.content,
                'model': openai_model,
                'status': 'success'
            }
            logger.info(f"OpenAI response length: {len(openai_response.choices[0].message.content)} chars")
        except Exception as e:
            logger.error(f"OpenAI API call failed with error: {str(e)}")
            results['openai'] = handle_api_error(e, 'openai', 'OpenAI')
    
    # Anthropic
    if api_keys.get('anthropic'):
        logger.info("Attempting Anthropic API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
            # Direct API call for Anthropic instead of client
            api_key = api_keys['anthropic']['key']
            anthropic_model = api_keys['anthropic'].get('model', 'claude-3-opus-20240229')
            logger.info(f"Using Anthropic model: {anthropic_model}")
            
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
            
            logger.info("Sending request to Anthropic API...")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            logger.info("Anthropic API call successful!")
            
            results['anthropic'] = {
                'content': response_data['content'][0]['text'],
                'model': anthropic_model,
                'status': 'success'
            }
            logger.info(f"Anthropic response length: {len(response_data['content'][0]['text'])} chars")
        except Exception as e:
            logger.error(f"Anthropic API call failed with error: {str(e)}")
            results['anthropic'] = handle_api_error(e, 'anthropic', 'Anthropic')
            
    # DeepSeek - using requests directly
    if api_keys.get('deepseek'):
        logger.info("Attempting DeepSeek API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
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
            logger.info(f"Sending request to DeepSeek API with model {deepseek_model}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            response_data = response.json()
            
            results['deepseek'] = {
                'content': response_data['choices'][0]['message']['content'],
                'model': deepseek_model,
                'status': 'success'
            }
            logger.info(f"DeepSeek response length: {len(response_data['choices'][0]['message']['content'])} chars")
        except Exception as e:
            logger.error(f"DeepSeek API call failed with error: {str(e)}")
            results['deepseek'] = handle_api_error(e, 'deepseek', 'DeepSeek')
            
    # Mistral (if present)
    if api_keys.get('mistral'):
        logger.info("Attempting Mistral API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
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
            
            logger.info(f"Sending request to Mistral API with model {mistral_model}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            results['mistral'] = {
                'content': response_data['choices'][0]['message']['content'],
                'model': mistral_model,
                'status': 'success'
            }
            logger.info(f"Mistral response length: {len(response_data['choices'][0]['message']['content'])} chars")
        except Exception as e:
            logger.error(f"Mistral API call failed with error: {str(e)}")
            results['mistral'] = handle_api_error(e, 'mistral', 'Mistral AI')

    # Google Gemini (if present)
    if api_keys.get('gemini'):
        logger.info("Attempting Google Gemini API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
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
            model_errors = []
            
            for gemini_model in gemini_models:
                try:
                    logger.info(f"Trying Gemini model: {gemini_model}")
                    
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
                    
                    logger.info(f"Sending request to Gemini API with model {gemini_model}")
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    response_data = response.json()
                    logger.info(f"Gemini API call successful with model {gemini_model}!")
                    
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
                    logger.info(f"Gemini response length: {len(text_content)} chars")
                    success = True
                    break
                    
                except Exception as model_error:
                    model_errors.append(f"{gemini_model}: {str(model_error)}")
                    logger.warning(f"Failed with model {gemini_model}: {str(model_error)}")
                    continue
            
            if not success:
                error_msg = f"All Gemini models failed to generate a response. Errors: {', '.join(model_errors)}"
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Gemini API call failed with error: {str(e)}")
            results['gemini'] = handle_api_error(e, 'gemini', 'Google Gemini')
    
    # Cohere (if present)
    if api_keys.get('cohere'):
        logger.info("Attempting Cohere API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
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
            
            logger.info(f"Sending request to Cohere API with model {cohere_model}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            results['cohere'] = {
                'content': response_data['text'],
                'model': cohere_model,
                'status': 'success'
            }
            logger.info(f"Cohere response length: {len(response_data['text'])} chars")
        except Exception as e:
            logger.error(f"Cohere API call failed with error: {str(e)}")
            results['cohere'] = handle_api_error(e, 'cohere', 'Cohere')
            
    # Azure OpenAI (if present)
    if api_keys.get('azure'):
        logger.info("Attempting Azure OpenAI API call...")
        try:
            # Input validation
            if not query:
                raise ValueError("Query parameter is required")
                
            api_key = api_keys['azure']['key']
            endpoint = api_keys['azure'].get('endpoint', '')
            azure_model = api_keys['azure'].get('model', 'gpt-4')
            deployment_name = api_keys['azure'].get('deployment', 'gpt4')
            
            # Validate endpoint URL
            if not endpoint or not endpoint.startswith(('http://', 'https://')):
                raise ValueError("Invalid or missing Azure OpenAI endpoint URL")
            
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
            
            logger.info(f"Sending request to Azure OpenAI API with deployment {deployment_name}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            results['azure'] = {
                'content': response_data['choices'][0]['message']['content'],
                'model': azure_model,
                'status': 'success'
            }
            logger.info(f"Azure OpenAI response length: {len(response_data['choices'][0]['message']['content'])} chars")
        except Exception as e:
            logger.error(f"Azure OpenAI API call failed with error: {str(e)}")
            results['azure'] = handle_api_error(e, 'azure', 'Azure OpenAI')
    
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

@api_bp.route('/export', methods=['POST'])
@api_error_handler
def export_responses():
    """Export responses in various formats (JSON, CSV, Markdown)"""
    data = request.json
    query = data.get('query', '')
    responses = data.get('responses', {})
    format_type = data.get('format', 'json')
    include_summary = data.get('include_summary', True)
    
    if not query or not responses:
        return jsonify({
            'error': 'Query and responses are required',
            'status': 'error'
        }), 400
    
    logger.info(f"Exporting responses in {format_type} format")
    logger.info(f"Query: {query}")
    logger.info(f"Response models: {list(responses.keys())}")
    
    # Create metadata for the export
    export_data = {
        "metadata": {
            "query": query,
            "timestamp": int(time.time()),
            "export_id": str(uuid.uuid4()),
            "model_count": len(responses)
        }
    }
    
    # Handle different formats
    if format_type.lower() == 'json':
        # For JSON, just return the full data
        export_data["responses"] = responses
        
        # If there's a summary and it should be included
        if include_summary and data.get('summary'):
            export_data["summary"] = data.get('summary')
            
        return jsonify({
            'data': export_data,
            'format': 'json',
            'status': 'success'
        })
        
    elif format_type.lower() == 'markdown':
        # Generate markdown text
        markdown_text = f"# AI Spectrum Results\n\n"
        markdown_text += f"## Query\n\n{query}\n\n"
        
        # Add responses
        markdown_text += "## Model Responses\n\n"
        for model_id, response in responses.items():
            if response.get('status') == 'success':
                markdown_text += f"### {model_id.capitalize()} ({response.get('model', 'unknown')})\n\n"
                markdown_text += f"{response.get('content', '')}\n\n"
                markdown_text += "---\n\n"
        
        # Add summary if available
        if include_summary and data.get('summary'):
            summary = data.get('summary')
            if summary.get('status') == 'success':
                markdown_text += "## Summary Insights\n\n"
                markdown_text += f"{summary.get('content', '')}\n\n"
        
        # Add footer
        markdown_text += f"\n\n*Exported from AI Spectrum at {time.strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return jsonify({
            'data': markdown_text,
            'format': 'markdown',
            'status': 'success'
        })
        
    elif format_type.lower() == 'csv':
        # CSV is more challenging since we need to flatten nested data
        # For simplicity, we'll create a CSV with model, status, and response
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Query', 'Model', 'Model ID', 'Status', 'Response'])
        
        # Write data rows
        for model_id, response in responses.items():
            # Clean content for CSV (remove newlines, etc.)
            content = response.get('content', '')
            if content:
                # Replace newlines and quotes for CSV compatibility
                content = content.replace('\n', ' ').replace('\r', ' ').replace('"', '""')
            
            writer.writerow([
                query,
                model_id.capitalize(),
                response.get('model', 'unknown'),
                response.get('status', 'unknown'),
                content
            ])
        
        # Get the CSV data as a string
        csv_data = output.getvalue()
        output.close()
        
        return jsonify({
            'data': csv_data,
            'format': 'csv',
            'status': 'success'
        })
        
    else:
        # Unsupported format
        return jsonify({
            'error': f'Unsupported export format: {format_type}',
            'supported_formats': ['json', 'markdown', 'csv'],
            'status': 'error'
        }), 400

@api_bp.route('/summarize', methods=['POST'])
@api_error_handler
def summarize_insights():
    """Generate insights from multiple model responses"""
    logger.info("\n===== GENERATING INSIGHTS =====")
    data = request.json
    query = data.get('query', '')
    responses = data.get('responses', {})
    api_keys = data.get('api_keys', {})
    
    logger.info(f"Query: {query}")
    logger.info(f"Responses from models: {list(responses.keys())}")
    logger.info(f"API Keys provided: {list(api_keys.keys())}")
    
    # Input validation
    if not query:
        return jsonify({
            'summary': handle_api_error(
                ValueError("Query parameter is required"), 
                'meta-summarizer'
            )
        })
        
    if not responses:
        return jsonify({
            'summary': handle_api_error(
                ValueError("No responses provided to generate insights"), 
                'meta-summarizer'
            )
        })
    
    if len(responses) < 2:
        return jsonify({
            'summary': handle_api_error(
                ValueError("At least two model responses are required for meaningful comparison"), 
                'meta-summarizer'
            )
        })
    
    # Find the API key to use for summarization
    summarizer_key = None
    provider_used = None
    preferred_providers = ['openai', 'gemini', 'anthropic', 'mistral']
    
    for provider in preferred_providers:
        if provider in api_keys:
            summarizer_key = api_keys[provider]['key']
            provider_used = provider
            logger.info(f"Using {provider} API key for summarization")
            break
    
    if not summarizer_key:
        # Use the first available key
        first_provider = next(iter(api_keys))
        summarizer_key = api_keys[first_provider]['key']
        provider_used = first_provider
        logger.info(f"Using {first_provider} API key for summarization")
    
    # Generate the summary
    try:
        summarizer = ResponseSummarizer(summarizer_key)
        summary = summarizer.summarize(query, responses)
        logger.info(f"Summarization status: {summary.get('status')}")
        
        # Add metadata about which model was used
        summary['provider_used'] = provider_used
        summary['response_count'] = len(responses)
        summary['timestamp'] = int(time.time())
        summary['request_id'] = str(uuid.uuid4())
        
        return jsonify({
            'summary': summary
        })
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        return jsonify({
            'summary': handle_api_error(e, 'meta-summarizer', provider_used)
        })