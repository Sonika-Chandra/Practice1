from datetime import datetime, timezone

from flask_login import UserMixin
from pymongo import ASCENDING
from pymongo.collection import ReturnDocument

from db import db  # PyMongo database instance

users_collection = db['users']

# Mirrors Mongoose's `unique: true` on googleId/email
users_collection.create_index([('googleId', ASCENDING)], unique=True)
users_collection.create_index([('email', ASCENDING)], unique=True)


class User(UserMixin):
    """Thin wrapper around a user document, for use with Flask-Login."""

    def __init__(self, doc):
        self._doc = doc

    def get_id(self):
        # Flask-Login requires get_id() to return a string
        return str(self._doc['_id'])

    def __getattr__(self, name):
        try:
            return self._doc[name]
        except KeyError:
            raise AttributeError(name)

    def to_dict(self):
        data = dict(self._doc)
        data['_id'] = str(data['_id'])
        return data


def create_user(google_id, email, name=None, access_token=None,
                 refresh_token=None, token_expiry=None):
    now = datetime.now(timezone.utc)
    doc = {
        'googleId': google_id,
        'email': email,
        'name': name,
        'accessToken': access_token,
        'refreshToken': refresh_token,
        'tokenExpiry': token_expiry,
        'createdAt': now,
        'updatedAt': now
    }
    result = users_collection.insert_one(doc)
    doc['_id'] = result.inserted_id
    return User(doc)


def find_by_id(user_id):
    from bson import ObjectId
    from bson.errors import InvalidId
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return None
    doc = users_collection.find_one({'_id': object_id})
    return User(doc) if doc else None


def find_by_google_id(google_id):
    doc = users_collection.find_one({'googleId': google_id})
    return User(doc) if doc else None


def find_by_email(email):
    doc = users_collection.find_one({'email': email})
    return User(doc) if doc else None


def update_user(user_id, updates):
    from bson import ObjectId
    updates = {**updates, 'updatedAt': datetime.now(timezone.utc)}
    doc = users_collection.find_one_and_update(
        {'_id': ObjectId(user_id)},
        {'$set': updates},
        return_document=ReturnDocument.AFTER
    )
    return User(doc) if doc else None