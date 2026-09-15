import logging

from flask import Blueprint, jsonify, g
from pymongo.errors import PyMongoError

from models.assignment import assignments_collection  # PyMongo collection for "assignments"
from services.gmail_service import fetch_assignments

gmail_bp = Blueprint('gmail', __name__)

logger = logging.getLogger(__name__)


def serialize_assignment(doc):
    """Convert a MongoDB document into a JSON-serializable dict."""
    if not doc:
        return None
    doc['_id'] = str(doc['_id'])
    doc['userId'] = str(doc['userId'])
    return doc


@gmail_bp.route('/gmail/fetch', methods=['POST'])
def fetch():
    try:
        emails = fetch_assignments(g.user)
        new_count = 0

        for email in emails:
            result = assignments_collection.update_one(
                {'gmailId': email['gmailId']},   # search condition
                {'$setOnInsert': email},         # insert only if not exists
                upsert=True                      # enable upsert
            )

            if result.upserted_id is not None:
                logger.info('New assignment inserted: %s', email['gmailId'])
                new_count += 1
            else:
                logger.info('Duplicate skipped: %s', email['gmailId'])

        assignments = list(
            assignments_collection.find({'userId': g.user['_id']}).sort('createdAt', -1)
        )

        return jsonify({
            'message': f'{new_count} new assignments fetched',
            'assignments': [serialize_assignment(a) for a in assignments]
        })

    except PyMongoError as error:
        logger.error('Controller error: %s', error)
        return jsonify({'error': str(error)}), 500
    except Exception as error:
        logger.error('Controller error: %s', error)
        return jsonify({'error': str(error)}), 500