from bottle import route, run, request
import spotipy
from spotipy import oauth2
import csv
import sys
import spotifyKeys 

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = spotifyKeys.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = spotifyKeys.SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = "playlist-modify-public playlist-modify-private"
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

@route('/')
def index():
        
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code != url:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")

        return createAddPlaylist(access_token)

    else:
        return htmlForLoginButton()

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def createAddPlaylist(access_token):
    sp = spotipy.Spotify(access_token)
    results = sp.current_user()

    playlistName = input("Enter the name of your playlist: ")
    playlistDescription = input("Enter the description of your playlist: ")
    filePath = input("Enter the file path of csv file with URLs to import: ")

    with open(filePath, newline = '') as f:
        reader = csv.reader(f)
        data = list(reader)
    flat_data = [item for sublist in data for item in sublist]
    
    newPlaylist = sp.user_playlist_create(results['id'], playlistName, public=False, collaborative=True, description=playlistDescription)
    [sp.playlist_add_items(newPlaylist['id'], flat_data[i:i+100], position=None) for i in range(0, len(flat_data), 100)]

    return results


run(host='localhost', port=8080)
