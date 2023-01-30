import sys
sys.path.append('../')
import utils
import time


# User Input
browseId = input("Enter url or browseId:\n").split('/').pop()


# Setup API
api = utils.setup()


# Get artist
artist = api.get_artist(browseId)
print('\nArtist: "' + artist['name'] + '"')


# Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
if 'singles' in artist:
    if 'params' in artist['singles']:
        singles = api.get_artist_albums(artist['channelId'], artist['singles']['params'])
    else:
        singles = artist['singles']['results']

# Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
if 'albums' in artist:
    if 'params' in artist['albums']:
        albums = api.get_artist_albums(artist['channelId'], artist['albums']['params'])
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
    singleSongs = api.get_album(single['browseId'])['tracks']
    for song in singleSongs:
        print('     - "' + song['title'] + '"')
        fullBrowseIdList.append(song['videoId'])
for album in albums:
    print('\nAlbum: "' + album['title'] + '"')
    albumSongs = api.get_album(album['browseId'])['tracks']
    for song in albumSongs:
        print('     - "' + song['title'] + '"')
        fullBrowseIdList.append(song['videoId'])


# Add to #ToListen
print('\nAdding all to "#ToListen"...')
ytMusicPlaylists = api.get_library_playlists(limit=100)
for ytMusicPlaylist in ytMusicPlaylists:
    if (ytMusicPlaylist['title'] == "#ToListen"):
        api.add_playlist_items(
            playlistId=ytMusicPlaylist['playlistId'],
            videoIds=fullBrowseIdList
        )


print("\nAll finished! Thank you for waiting patiently you impatient prick.")
time.sleep(2.5)