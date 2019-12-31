import os
OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
OAUTH_REDIRECT_URI = os.environ['OAUTH_REDIRECT_URI']
API_KEY = os.environ['API_KEY']

google_auth_URL = "https://accounts.google.com/o/oauth2/v2/auth"
google_token_URL = "https://www.googleapis.com/oauth2/v4/token"
scope = [
	'https://www.googleapis.com/auth/photoslibrary.readonly'
]

from requests_oauthlib import OAuth2Session
google = OAuth2Session(OAUTH_CLIENT_ID, scope=scope, redirect_uri=OAUTH_REDIRECT_URI)
authorization_url, state = google.authorization_url(google_auth_URL, access_type="offline", prompt="select_account") 

print('Please authorize at:' + authorization_url)

