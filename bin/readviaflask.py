from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, session
from flask.json import jsonify
import os
import sys
import tempfile
import zipfile
import shutil

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

def createZipFile(file, name):
        zipname=tempfile.NamedTemporaryFile(suffix='.zip', delete=False).name
        zip = zipfile.ZipFile(zipname, 'w')
        zip.write(file, name)
        zip.close()

        return zipname

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
	moreAlbums=True
	pageToken=None
	albums = [] 
	while (moreAlbums):
		query='https://photoslibrary.googleapis.com/v1/albums'
		if (pageToken != None):	
			query = query+"?pageToken="+pageToken
		results=google.get(query).json()
		for a in results['albums']:
			albums.append(a)
		if 'nextPageToken' in results:
			pageToken=results['nextPageToken']
		else:
			moreAlbums=False	 

	print("There are: " + str(len(albums)) + " albums on this site.", file=sys.stdout)

	for album in albums:
		morePics=True
		pageToken=None
		pics = []
		album['mediaItems'] = []
		while (morePics):
			url='https://photoslibrary.googleapis.com/v1/mediaItems:search'
			if (pageToken != None):
				data = { 'albumId': album['id'], 'pageToken': pageToken }
			else:
				data = { 'albumId': album['id'] }

			results=google.post(url=url, data=data).json()
			for a in results['mediaItems']:
				album['mediaItems'].append(a)
				if 'nextPageToken' in results:
					pageToken=results['nextPageToken']
				else:
					morePics=False	
		print("There are: " + str(len(album['mediaItems'])) + " media items in album: " + album['title'])


	root="/Users/fultonm/Downloads/tmpgoogle/"
	for album in albums:
		outdir=root + album['title']
		try:
			os.makedirs(outdir)
		except PermissionError as e:
			print(str(e))
			print("Unable to create output directory: " + outdir)
			return "Fail."
		except FileExistsError:
			pass

		for mediaItem in album['mediaItems']:
			if (mediaItem['mimeType'] == 'image/jpeg'):
				results = google.get(mediaItem['baseUrl'], stream=True)
				if results.status_code == 200:
					file=outdir + "/" + mediaItem['filename']
					print(album['title'] + ": " + mediaItem['filename'])
					with open(file, 'wb') as f:
						results.raw.decode_content = True
						shutil.copyfileobj(results.raw, f)

	return "Done."
	
	

if __name__ == "__main__":
	# This allows us to use a plain HTTP callback
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

	app.config['SESSION_TYPE'] = 'filesystem'
	app.run()
