from flask import Blueprint

from controllers import ai_controller
from middleware.auth import require_authentication

ai_bp = Blueprint('ai', __name__)

ai_bp.before_request(require_authentication)

ai_bp.add_url_rule('/analyze', view_func=ai_controller.analyze, methods=['POST'])
ai_bp.add_url_rule('/plan', view_func=ai_controller.plan, methods=['POST'])