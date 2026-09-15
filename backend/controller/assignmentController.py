from flask import Blueprint, request, jsonify, g
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from models.assignment import assignments_collection  # PyMongo collection for "assignments"

assignment_bp = Blueprint('assignment', __name__)


def serialize_assignment(doc):
    """Convert a MongoDB document into a JSON-serializable dict."""
    if not doc:
        return None
    doc['_id'] = str(doc['_id'])
    doc['userId'] = str(doc['userId'])
    return doc


@assignment_bp.route('/assignments', methods=['POST'])
def create():
    try:
        data = request.get_json() or {}
        data['userId'] = g.user['_id']

        result = assignments_collection.insert_one(data)
        assignment = assignments_collection.find_one({'_id': result.inserted_id})

        return jsonify(serialize_assignment(assignment)), 201
    except PyMongoError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        return jsonify({'error': str(error)}), 400


@assignment_bp.route('/assignments', methods=['GET'])
def get_all():
    try:
        assignments = list(assignments_collection.find({'userId': g.user['_id']}))
        return jsonify([serialize_assignment(a) for a in assignments])
    except PyMongoError as error:
        return jsonify({'error': str(error)}), 500


@assignment_bp.route('/assignments/<id>', methods=['GET'])
def get_by_id(id):
    try:
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return jsonify({'error': 'Assignment not found'}), 404

        assignment = assignments_collection.find_one({
            '_id': object_id,
            'userId': g.user['_id']
        })

        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404

        return jsonify(serialize_assignment(assignment))
    except PyMongoError as error:
        return jsonify({'error': str(error)}), 500


@assignment_bp.route('/assignments/<id>', methods=['PUT', 'PATCH'])
def update(id):
    try:
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return jsonify({'error': 'Assignment not found'}), 404

        data = request.get_json() or {}

        result = assignments_collection.find_one_and_update(
            {'_id': object_id, 'userId': g.user['_id']},
            {'$set': data},
            return_document=True
        )

        if not result:
            return jsonify({'error': 'Assignment not found'}), 404

        return jsonify(serialize_assignment(result))
    except PyMongoError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        return jsonify({'error': str(error)}), 400


@assignment_bp.route('/assignments/<id>', methods=['DELETE'])
def delete(id):
    try:
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return jsonify({'error': 'Assignment not found'}), 404

        assignment = assignments_collection.find_one_and_delete({
            '_id': object_id,
            'userId': g.user['_id']
        })

        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404

        return jsonify({'message': 'Assignment deleted'})
    except PyMongoError as error:
        return jsonify({'error': str(error)}), 500