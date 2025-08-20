# auth_service.py
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/userinfo.email", "openid"]
#SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "openid"]
USER_DATA_FILE = "user_data.json"
#REDIRECT_URI = "http://127.0.0.1:5000/oauth2callback"
REDIRECT_URI = "https://mushtastic-intelligence.com/oauth2callback"

def start_google_auth_flow():
    """Start the Google OAuth flow and return the authorization URL."""
    flow = Flow.from_client_secrets_file(
        "new_login_client_id.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='select_account consent')
    return auth_url, state  # Return only what’s needed

def complete_google_auth_flow(code):
    """Complete the OAuth flow with the authorization code."""
    flow = Flow.from_client_secrets_file(
        "new_login_client_id.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return build("oauth2", "v2", credentials=credentials)

def refresh_user_data():
    """Refresh user data daily by clearing if older than 24 hours."""
    current_time = datetime.now()
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
            last_updated = datetime.strptime(data.get('last_updated', '1970-01-01'), '%Y-%m-%d')
            if current_time - last_updated > timedelta(days=1):
                data = {'users': {}, 'last_updated': current_time.strftime('%Y-%m-%d')}
                with open(USER_DATA_FILE, 'w') as f:
                    json.dump(data, f)
        except (json.JSONDecodeError, ValueError):
            data = {'users': {}, 'last_updated': current_time.strftime('%Y-%m-%d')}
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(data, f)
    else:
        data = {'users': {}, 'last_updated': current_time.strftime('%Y-%m-%d')}
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f)
    return data

def store_user_data(google):
    """Store or update user data after authentication for multiple users."""
    user_info = google.userinfo().get().execute()
    user_id = user_info['id']
    user_email = user_info['email']

    user_data = refresh_user_data()
    user_data['users'][user_id] = {
        'email': user_email,
        'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    user_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=4)
    return user_id
