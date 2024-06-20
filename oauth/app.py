from flask import Flask, url_for, session
from authlib.integrations.flask_client import OAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
oauth = OAuth(app)

# Google OAuth Configuration
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/login/authorized/google',
    client_kwargs={'scope': 'openid profile email'}
)

# Spotify OAuth Configuration
spotify = oauth.register(
    name='spotify',
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    authorize_url='https://accounts.spotify.com/authorize',
    authorize_params=None,
    access_token_url='https://accounts.spotify.com/api/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/login/authorized/spotify',
    client_kwargs={'scope': 'user-library-read'}
)

# LinkedIn OAuth Configuration
linkedin = oauth.register(
    name='linkedin',
    client_id=os.getenv('LINKEDIN_CLIENT_ID'),
    client_secret=os.getenv('LINKEDIN_CLIENT_SECRET'),
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    authorize_params=None,
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:5000/login/authorized/linkedin',
    client_kwargs={'scope': 'r_liteprofile r_emailaddress'}
)

@app.route('/')
def index():
    return 'Welcome to the OAuth Integration Example'

@app.route('/login/<provider>')
def login(provider):
    if provider == 'google':
        redirect_uri = url_for('authorized', provider='google', _external=True)
        return google.authorize_redirect(redirect_uri)
    elif provider == 'spotify':
        redirect_uri = url_for('authorized', provider='spotify', _external=True)
        return spotify.authorize_redirect(redirect_uri)
    elif provider == 'linkedin':
        redirect_uri = url_for('authorized', provider='linkedin', _external=True)
        return linkedin.authorize_redirect(redirect_uri)

@app.route('/login/authorized/<provider>')
def authorized(provider):
    if provider == 'google':
        token = oauth.google.authorize_access_token()
        response = oauth.google.get('userinfo')
    elif provider == 'spotify':
        token = oauth.spotify.authorize_access_token()
        response = oauth.spotify.get('me')
    elif provider == 'linkedin':
        token = oauth.linkedin.authorize_access_token()
        response = oauth.linkedin.get('me')

    session['oauth_token'] = token
    return 'Logged in as: ' + provider + '<br>' + str(response.json())

if __name__ == '__main__':
    app.run(debug=True)