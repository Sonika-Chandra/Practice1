import os
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required

from extensions import oauth, login_manager
from models import user as user_model

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# Equivalent of the Passport GoogleStrategy registration
google = oauth.register(
    name='google',
    client_id=os.environ['GMAIL_CLIENT_ID'],
    client_secret=os.environ['GMAIL_CLIENT_SECRET'],
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'profile email https://www.googleapis.com/auth/gmail.readonly'
    }
)


# Equivalent of passport.deserializeUser
@login_manager.user_loader
def load_user(user_id):
    return user_model.find_by_id(user_id)


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/google')
def google_login():
    redirect_uri = os.environ['GMAIL_REDIRECT_URI']
    # prompt='consent' forces the consent screen to show scopes, same as the JS version
    return google.authorize_redirect(redirect_uri, prompt='consent')


@auth_bp.route('/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
    except Exception:
        return redirect('/')

    profile = google.get('userinfo').json()
    access_token = token.get('access_token')
    refresh_token = token.get('refresh_token')
    token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    # Equivalent of the verify callback passed into GoogleStrategy
    existing = user_model.find_by_google_id(profile['id'])
    if existing is None:
        account = user_model.create_user(
            google_id=profile['id'],
            email=profile['email'],
            name=profile.get('name'),
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry
        )
    else:
        account = user_model.update_user(existing.get_id(), {
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'tokenExpiry': token_expiry
        })

    login_user(account)  # equivalent of passport's done(null, user)
    return redirect(f'{FRONTEND_URL}/dashboard')


@auth_bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
    except Exception:
        return jsonify({'error': 'Logout failed'}), 500
    return redirect(FRONTEND_URL)


@auth_bp.route('/user')
def get_user():
    if current_user.is_authenticated:
        return jsonify({'user': current_user.to_dict()})
    return jsonify({'error': 'Not authenticated'}), 401