import time
from ytmusicapi import YTMusic
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Setup
stopwatchStart = time.perf_counter()
ytMusicApi = YTMusic('C:/auth/YTMusicManager/ytMusicApiHeaders.json')
firebase_admin.initialize_app( credentials.Certificate('C:/auth/YTMusicManager/ytMusicFirebaseKey.json') )
db = firestore.client()


# User Input
browseId = input("Enter url or browseId:\n").split('/').pop()

# Get artist
artist = ytMusicApi.get_artist(browseId)
print('\nArtist: "' + artist['name'] + '"')


# Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
if 'singles' in artist:
    if 'params' in artist['singles']:
        singles = ytMusicApi.get_artist_albums(artist['channelId'], artist['singles']['params'])
    else:
        singles = artist['singles']['results']

# Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
if 'albums' in artist:
    if 'params' in artist['albums']:
        albums = ytMusicApi.get_artist_albums(artist['channelId'], artist['albums']['params'])
    else:
        albums = artist['albums']['results']


# IF no singles
try: singles
except NameError:
    singles = []
    print("Artist does not have any singles.")

# IF no albums
try: albums
except NameError:
    albums = []
    print("Artist does not have any albums.")


# Reverse lists so in date order asc
singles = singles[::-1]
albums = albums[::-1]


# Create list of all singles' and albums' browseId's
fullBrowseIdList = []
for single in singles:
    print('\nSingle: "' + single['title'] + '"')
    singleSongs = ytMusicApi.get_album(single['browseId'])['tracks']
    for song in singleSongs:
        print('     - "' + song['title'] + '"')
        fullBrowseIdList.append(song['videoId'])
for album in albums:
    print('\nAlbum: "' + album['title'] + '"')
    albumSongs = ytMusicApi.get_album(album['browseId'])['tracks']
    for song in albumSongs:
        print('     - "' + song['title'] + '"')
        fullBrowseIdList.append(song['videoId'])


# Add to #ToListen
print('\nAdding all to "#ToListen"...')
ytMusicPlaylists = ytMusicApi.get_library_playlists(limit=100)
for ytMusicPlaylist in ytMusicPlaylists:
    if (ytMusicPlaylist['title'] == "#ToListen"):
        ytMusicApi.add_playlist_items(
            playlistId=ytMusicPlaylist['playlistId'],
            videoIds=fullBrowseIdList,
            duplicates=True
        )


print("\nAll finished! Thank you for waiting patiently you impatient prick.")
time.sleep(2.5)