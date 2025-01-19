import os

from functools import wraps
from flask import jsonify

API_KEY = os.getenv("API_KEY")
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',           # Or restrict to specific domain
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '3600',
}


def api_key_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        api_key = request.form.get("api_key")  # Extract API key from the request
        if api_key != API_KEY:
            return (jsonify({"error": "Invalid API key"}), 403, CORS_HEADERS)  # Forbidden status
        return f(request, *args, **kwargs)  # Call the original function
    return decorated_function
