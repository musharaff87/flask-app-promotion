# auth_service.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "openid"]
USER_DATA_FILE = "user_data.json"

def authenticate_google():
    """Authenticate with Google for login, always prompting for a new flow."""
    flow = InstalledAppFlow.from_client_secrets_file("client_secret_2.json", SCOPES)
    credentials = flow.run_local_server(port=8080)
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