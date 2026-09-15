from flask import Blueprint

from controllers import assignment_controller
from middleware.auth import require_authentication

assignment_bp = Blueprint('assignment', __name__)

assignment_bp.before_request(require_authentication)

assignment_bp.add_url_rule('/', view_func=assignment_controller.create, methods=['POST'])
assignment_bp.add_url_rule('/', view_func=assignment_controller.get_all, methods=['GET'])
assignment_bp.add_url_rule('/<id>', view_func=assignment_controller.get_by_id, methods=['GET'])
assignment_bp.add_url_rule('/<id>', view_func=assignment_controller.update, methods=['PUT'])
assignment_bp.add_url_rule('/<id>', view_func=assignment_controller.delete, methods=['DELETE'])