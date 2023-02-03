import sys
sys.path.append('../')
import utils
import time


# Setup
api = utils.setup()

# Get all playlists

# Get saved data for last checks
with open('data.txt') as f:
    lastChecked = f.read().splitlines()

# Setup albums and singles list to add to #ToListen
albumsSinglesIdList = []
# Setup new artists list to save at end
updatedArtists = []

# Setup totals to display at end
totalNewArtists = []
totalNewSinglesAlbums = []

# For each artist
for artistLine in artists:

    print("")

    # Get elements
    artistElements = artistLine.split('|--|')
    
    # IF only one element, new artist, so just get latest single and album
    if (len(artistElements) <= 1):

        artistId = artistLine.split('/').pop()

        # Get artist
        artist = api.get_artist(artistId)
        print("New artist: " + artist['name'])
        totalNewArtists.append(artist['name'])
        
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
        print("Checking: " + artistName)
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
                totalNewSinglesAlbums.append(artist['name'] + ' - ' + album['title'] + " (Album)")

        # Make list of all singles up until last checked album
        for single in singles:
            if single['browseId'] == lastSingleId:
                break
            else:
                print("New single: " + single['title'])
                albumsSinglesIdList.append(single['browseId'])
                totalNewSinglesAlbums.append(artist['name'] + ' - ' + album['title'] + " (Single)")
                
        # Add new artist to updated artists list
        updatedArtists.append(artist['name'] + "|--|" + artistId + "|--|" + albums[0]['browseId'] + "|--|" + singles[0]['browseId'])


# Print final new artists
print("\n\n= = = = = = = = = = =\n")
if (len(totalNewArtists) > 0):
    print("New artists:\n")
    for newArtist in totalNewArtists:
        print("     " + newArtist)
else:
    print("No new artists.")
print("\n= = = = = = = = = = =\n")
time.sleep(1)
# Print final new singles and albums
if (len(totalNewSinglesAlbums) > 0):
    print("New singles and albums:\n")
    for newSingleAlbum in totalNewSinglesAlbums:
        print("     " + newSingleAlbum)
else:
    print("No new songs.")
print("\n= = = = = = = = = = =\n\n")
time.sleep(1)

# Add to #ToListen
if (len(totalNewSinglesAlbums) > 0):
    print('Adding all to "#ToListen"...\n')
fullBrowseIdList = []
for albumSingle in albumsSinglesIdList:
    songsList = api.get_album(albumSingle)['tracks']
    for song in songsList:
        fullBrowseIdList.append(song['videoId'])
if len(fullBrowseIdList) > 0:
    ytMusicPlaylists = api.get_library_playlists(limit=100)
    for ytMusicPlaylist in ytMusicPlaylists:
        if (ytMusicPlaylist['title'] == "#ToListen"):
            api.add_playlist_items(
                playlistId=ytMusicPlaylist['playlistId'],
                videoIds=fullBrowseIdList
            )


# Update 'artists.txt'
f = open('artists.txt', 'w')
for artist in updatedArtists:
    f.write(artist + "\n")
f.close()


print("All finished! Thank you for waiting patiently you impatient prick.");
time.sleep(600);