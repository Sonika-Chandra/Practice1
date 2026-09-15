from flask import Blueprint

from controllers import gmail_controller
from middleware.auth import require_authentication

gmail_bp = Blueprint('gmail', __name__)

gmail_bp.before_request(require_authentication)

gmail_bp.add_url_rule('/fetch', view_func=gmail_controller.fetch, methods=['GET'])