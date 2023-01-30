import sys
sys.path.append('../')
import utils
import time


# Setup
api = utils.setup()

# Get artists from 'artists.txt'
with open('artists.txt') as f:
    artists = f.read().splitlines()

# Setup albums and singles list to add to #ToListen
albumsSinglesIdList = []
# Setup new artists list to save at end
updatedArtists = []

# For each artist
for artistLine in artists:

    # Get elements
    artistElements = artistLine.split('|--|')
    
    # IF only one element, new artist, so just get latest single and album
    if (len(artistElements) <= 1):

        artistId = artistLine.split('/').pop()

        # Get artist
        artist = api.get_artist(artistId)
        print("New artist: " + artist['name'])
        
        # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
        if 'albums' in artist:
            if 'params' in artist['albums']:
                albums = api.get_artist_albums(artist['channelId'], artist['albums']['params'])
            else:
                albums = artist['albums']['results']
        try: albums
        except NameError:
            albums = []
            print("Artist does not have any albums.")

        # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
        if 'singles' in artist:
            if 'params' in artist['singles']:
                singles = api.get_artist_albums(artist['channelId'], artist['singles']['params'])
            else:
                singles = artist['singles']['results']
        try: singles
        except NameError:
            singles = []
            print("Artist does not have any singles.")
        
        # Add new artist to updated artists list
        updatedArtists.append(artist['name'] + "|--|" + artistId + "|--|" + albums[0]['browseId'] + "|--|" + singles[0]['browseId'])

    # ELSE do check on artist
    else:

        # Get elements
        artistName = artistElements[0]
        artistId = artistElements[1]
        lastAlbumId = artistElements[2]
        lastSingleId = artistElements[3]

        # Get artist
        print("Checking: " + artistName + "...")
        artist = api.get_artist(artistId)

        # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
        if 'albums' in artist:
            if 'params' in artist['albums']:
                albums = api.get_artist_albums(artist['channelId'], artist['albums']['params'])
            else:
                albums = artist['albums']['results']
        try: albums
        except NameError:
            albums = []
            print("Artist does not have any albums.")

        # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
        if 'singles' in artist:
            if 'params' in artist['singles']:
                singles = api.get_artist_albums(artist['channelId'], artist['singles']['params'])
            else:
                singles = artist['singles']['results']
        try: singles
        except NameError:
            singles = []
            print("Artist does not have any singles.")

        # Make list of all albums up until last checked album
        for album in albums:
            if album['browseId'] == lastAlbumId:
                break
            else:
                print("New album: " + album['title'])
                albumsSinglesIdList.append(album['browseId'])

        # Make list of all singles up until last checked album
        for single in singles:
            if single['browseId'] == lastSingleId:
                break
            else:
                print("New single: " + single['title'])
                albumsSinglesIdList.append(single['browseId'])
                
        # Add new artist to updated artists list
        updatedArtists.append(artist['name'] + "|--|" + artistId + "|--|" + albums[0]['browseId'] + "|--|" + singles[0]['browseId'])


# Add all new albums and singles to #ToListen
fullBrowseIdList = []
for albumSingle in albumsSinglesIdList:
    songsList = api.get_album(albumSingle)['tracks']
    for song in songsList:
        fullBrowseIdList.append(song['videoId'])


# Add to #ToListen
if len(fullBrowseIdList) > 0:
    print('\nAdding all to "#ToListen"...')
    ytMusicPlaylists = api.get_library_playlists(limit=100)
    for ytMusicPlaylist in ytMusicPlaylists:
        if (ytMusicPlaylist['title'] == "#ToListen"):
            api.add_playlist_items(
                playlistId=ytMusicPlaylist['playlistId'],
                videoIds=fullBrowseIdList
            )
else:
    print("No songs to add.")

# Update 'artists.txt'
f = open('artists.txt', 'w')
for artist in updatedArtists:
    f.write(artist + "\n")
f.close()