from flask import Flask, redirect, url_for, session, request, jsonify
from requests_oauthlib import OAuth2Session
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# OAuth2 client setup
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = 'http://localhost:5000/callback'

# Scopes for accessing Google APIs
google_scopes = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/contacts.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/gmail.readonly'
]

# Load service account credentials
credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
credentials = service_account.Credentials.from_service_account_file(credentials_path)

@app.route('/')
def home():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=google_scopes)
    authorization_url, state = google.authorization_url(authorization_base_url, access_type="offline")
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    google = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    try:
        token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
        session['oauth_token'] = token
        return redirect(url_for('.profile'))
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/profile')
def profile():
    google = OAuth2Session(client_id, token=session['oauth_token'])
    try:
        response = google.get('https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses')
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/google/calendar')
def google_calendar():
    google = OAuth2Session(client_id, token=session['oauth_token'])
    try:
        response = google.get('https://www.googleapis.com/calendar/v3/calendars')
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/google/contacts')
def google_contacts():
    google = OAuth2Session(client_id, token=session['oauth_token'])
    try:
        response = google.get('https://www.google.com/m8/feeds/contacts/default/full')
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/google/drive')
def google_drive():
    google = OAuth2Session(client_id, token=session['oauth_token'])
    try:
        response = google.get('https://www.googleapis.com/drive/v3/files')
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/google/gmail')
def google_gmail():
    google = OAuth2Session(client_id, token=session['oauth_token'])
    try:
        response = google.get('https://www.googleapis.com/gmail/v1/users/me/messages')
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return jsonify(error=str(e)), 403

if __name__ == "__main__":
    app.run(debug=True)