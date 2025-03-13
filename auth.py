from functools import wraps
from flask import request, jsonify

# For simplicity, using a hardcoded token
# In a production environment, you would use a more secure approach
VALID_TOKEN = "secret-token-123"

def token_required(f):
    """Decorator for token-based authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Authentication token is missing!'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'message': 'Invalid authentication token format!'}), 401
        
        if token != VALID_TOKEN:
            return jsonify({'message': 'Invalid authentication token!'}), 401
            
        return f(*args, **kwargs)
    
    return decorated
