from pathlib import Path
import configparser
from functools import wraps
from flask import jsonify

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # Or restrict to specific domain
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "3600",
}

config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / "options.ini")
PUURLEE_API_KEY = config["Puurlee"]["apikey"]
OPENAI_API_KEY = config["OpenAI"]["apikey"]
PINECONE_API_KEY = config["Pinecone"]["apikey"]


def api_key_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        api_key = request.form.get("api_key")  # Extract API key from the request
        if api_key != PUURLEE_API_KEY:
            return (
                jsonify({"error": "Invalid API key"}),
                403,
                CORS_HEADERS,
            )  # Forbidden status
        return f(request, *args, **kwargs)  # Call the original function

    return decorated_function
