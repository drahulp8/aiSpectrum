"""
Centralized error handling for the AI Spectrum application.
Provides standardized error responses and logging for API errors.
"""
import logging
import time
import traceback
import uuid
from functools import wraps
from flask import jsonify, request

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('aiSpectrum')

# Error types and codes
ERROR_TYPES = {
    'AUTH_ERROR': {
        'code': 'auth_error',
        'status_code': 401,
        'message': 'Authentication failed. Please check your API key.'
    },
    'RATE_LIMIT': {
        'code': 'rate_limit',
        'status_code': 429,
        'message': 'Rate limit exceeded. Please try again later.'
    },
    'MODEL_NOT_FOUND': {
        'code': 'model_not_found',
        'status_code': 404,
        'message': 'The specified AI model was not found.'
    },
    'INVALID_REQUEST': {
        'code': 'invalid_request',
        'status_code': 400,
        'message': 'Invalid request parameters.'
    },
    'SERVER_ERROR': {
        'code': 'server_error',
        'status_code': 500,
        'message': 'An internal server error occurred.'
    },
    'API_ERROR': {
        'code': 'api_error',
        'status_code': 502,
        'message': 'Error communicating with the AI provider API.'
    }
}

def handle_api_error(error, model_id, api_provider=None):
    """
    Process API errors and return standardized responses
    
    Args:
        error: The exception object
        model_id: The model identifier (e.g., 'openai', 'anthropic')
        api_provider: Optional provider name for logging
        
    Returns:
        dict: Standardized error response
    """
    error_str = str(error)
    error_type = 'API_ERROR'
    error_details = error_str
    request_id = str(uuid.uuid4())
    
    # Determine error type based on error message
    if any(key in error_str.lower() for key in ['unauthorized', 'invalid key', 'authentication', 'auth']):
        error_type = 'AUTH_ERROR'
    elif any(key in error_str.lower() for key in ['rate limit', 'too many requests', 'quota']):
        error_type = 'RATE_LIMIT'
    elif any(key in error_str.lower() for key in ['model not found', 'does not exist', 'invalid model']):
        error_type = 'MODEL_NOT_FOUND'
    elif any(key in error_str.lower() for key in ['bad request', 'invalid request', 'missing field']):
        error_type = 'INVALID_REQUEST'
    
    # Sanitize API keys from error messages for security
    if api_provider and 'key' in error_str.lower():
        # Mask any potential API key in the error message
        import re
        # Look for patterns like 'key-1234' or 'sk-1234'
        key_pattern = r'([a-zA-Z]+-[a-zA-Z0-9]{4,})'
        error_details = re.sub(key_pattern, '[API_KEY_MASKED]', error_str)
    
    # Log the error with context
    logger.error(f"API Error ({error_type}) - Provider: {api_provider}, Model: {model_id}, Request ID: {request_id}")
    logger.error(f"Error details: {error_details}")
    
    # Return standardized error response
    return {
        'content': f"Error: {ERROR_TYPES[error_type]['message']}",
        'error_code': ERROR_TYPES[error_type]['code'],
        'error_details': error_details,
        'request_id': request_id,
        'timestamp': int(time.time()),
        'model': model_id,
        'status': 'error'
    }

def api_error_handler(f):
    """
    Decorator for API routes to standardize error handling
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Unhandled exception in API route: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': ERROR_TYPES['SERVER_ERROR']['message'],
                'error_code': ERROR_TYPES['SERVER_ERROR']['code'],
                'timestamp': int(time.time()),
                'request_id': str(uuid.uuid4())
            }), ERROR_TYPES['SERVER_ERROR']['status_code']
    
    return decorated_function