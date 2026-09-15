from functools import wraps

from flask import jsonify, g
from flask_login import current_user


def is_authenticated(f):
    """Route decorator equivalent of the Express isAuthenticated middleware."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            g.user = current_user
            return f(*args, **kwargs)
        return jsonify({'error': 'Not authenticated'}), 401
    return decorated