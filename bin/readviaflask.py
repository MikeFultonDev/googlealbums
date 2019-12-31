from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, session
from flask.json import jsonify
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

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

@app.route("/")
def demo():
	google = OAuth2Session(OAUTH_CLIENT_ID, scope=scope, redirect_uri=OAUTH_REDIRECT_URI)
	authorization_url, state = google.authorization_url(google_auth_URL, access_type="offline", prompt="select_account")

# State is used to prevent CSRF, keep this for later.
	session['oauth_state'] = state
	return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():

	google = OAuth2Session(OAUTH_CLIENT_ID, state=session['oauth_state'], redirect_uri=OAUTH_REDIRECT_URI)
	token = google.fetch_token(google_token_URL, client_secret=OAUTH_CLIENT_SECRET, authorization_response=request.url)
	session['oauth_token'] = token

	return redirect(url_for('.listalbum'))

@app.route("/listalbum", methods=["GET"])
def listalbum():
	google = OAuth2Session(OAUTH_CLIENT_ID, token=session['oauth_token'])
	return jsonify(google.get('https://photoslibrary.googleapis.com/v1/albums').json())

if __name__ == "__main__":
	# This allows us to use a plain HTTP callback
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

	app.config['SESSION_TYPE'] = 'filesystem'
	app.run()
