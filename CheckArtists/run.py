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

# Playlists to add artists from
playlistsToAddFrom = [
    '2014',
    '27Club',
    'AfterDark',
    'Ambient',
    'Calvin',
    'Classics',
    'Ferris',
    'Goodies',
    'Jaaaazz',
    'Jesse',
    'John Wick',
    'Katy',
    'MG',
    'NFS',
    'Orchestra',
    'Playlist 2',
    'Snake',
    'The Doc',
    'z'
]

# Get all artists from my playlists
artistsToCheck = []
print("\nGetting artists from:\n")
playlistsBrief = ytMusicApi.get_library_playlists(limit=100)
for playlistBrief in playlistsBrief:
    # IF is a playlist to check
    if playlistBrief['title'] in playlistsToAddFrom:
        print("     - " + playlistBrief['title'])
        playlist = ytMusicApi.get_playlist(playlistBrief['playlistId'], limit=None)
        # FOR EACH track
        for track in playlist['tracks']:
            # IF track is an official song
            if track['album'] is not None:
                # FOR EACH artist in track
                for artist in track['artists']:
                    # IF artist not in 'artistsToCheck' AND has an id AND not my own uploaded song, add
                    if not any(item['id'] == artist['id'] for item in artistsToCheck) and artist['id'] is not None and 'privately_owned_artist' not in artist['id']:
                        artistsToCheck.append(artist)

# Sort alphabetically by artist name
artistsToCheck.sort(key=lambda artist: artist['name'])

print(f"\nArtists to check: {len(artistsToCheck)}")
print("\n\n= = = = = = = = = = =\n")

# Get checked data
checkedCollection = db.collection('LastChecked')
checkedDocs = checkedCollection.get()

# Setup albums and singles list to add to #ToListen
albumsSinglesIdList = []
# Setup new artist docs list to save at end
updatedArtists = []

# Setup totals to display at end
totalNewArtists = []
totalNewSinglesAlbums = []
totalArtistErrors = []

# For each artist
for artistBrief in artistsToCheck:

    try:
        # Reset
        artist = None
        artistCheckedDoc = None
        artistElements = None
        albums = []
        singles = []
        newAlbums = []
        newSingles = []
        albumText = None
        singleText = None

        print("")

        print(f"Checking: {artistBrief['name']}")

        # Get checked record for artist
        for record in checkedDocs:
            if record is not None and record._data['artistId'] == artistBrief['id']:
                artistCheckedDoc = record
                break
        
        # IF found record, check artist
        if artistCheckedDoc is not None:

            # Get artist
            artist = ytMusicApi.get_artist(artistBrief['id'])

            # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'albums' in artist:
                if 'params' in artist['albums']:
                    albums = ytMusicApi.get_artist_albums(artist['channelId'], artist['albums']['params'])
                else:
                    albums = artist['albums']['results']
            try: albums
            except NameError:
                albums = []

            # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'singles' in artist:
                if 'params' in artist['singles']:
                    singles = ytMusicApi.get_artist_albums(artist['channelId'], artist['singles']['params'])
                else:
                    singles = artist['singles']['results']
            try: singles
            except NameError:
                singles = []

            # Find new albums
            for album in albums:
                if album['browseId'] not in artistCheckedDoc._data['checkedAlbums']:
                    newAlbums.append(album)

            # Find new singles
            for single in singles:
                if single['browseId'] not in artistCheckedDoc._data['checkedSingles']:
                    newSingles.append(single)

            # Add new albums, unless there are too many which means ytmusic changed something that fucked me over
            if (len(newAlbums) > 0 and len(newAlbums) < 5):
                for newAlbum in newAlbums:
                    print("New album: " + newAlbum['title'])
                    albumsSinglesIdList.append(newAlbum['browseId'])
                    totalNewSinglesAlbums.append(artistBrief['name'] + ' - ' + newAlbum['title'] + " (Album)")
            elif (len(newAlbums) > 5):
                print("Too many albums!\nSkipping these albums and resetting this artist's checked albums.")

            # Add new singles, unless there are too many which means ytmusic changed something that fucked me over
            if (len(newSingles) > 0 and len(newSingles) < 5):
                for newSingle in newSingles:
                    print("New single: " + newSingle['title'])
                    albumsSinglesIdList.append(newSingle['browseId'])
                    totalNewSinglesAlbums.append(artistBrief['name'] + ' - ' + newSingle['title'] + " (Single)")
            elif (len(newSingles) > 5):
                print("Too many singles!\nSkipping these singles and resetting this artist's checked singles.")

            # Add to 'updatedArtists' to update Checked doc later using id
            if (len(newAlbums) > 0 or len(newSingles) > 0):
                artistCheckedDoc._data['checkedAlbums'] = [album['browseId'] for album in albums]
                artistCheckedDoc._data['checkedSingles'] = [single['browseId'] for single in singles]
                updatedArtists.append(artistCheckedDoc)

        # ELSE is new, so just get latest single and album
        else:

            print("New Artist!")

            # Get artist
            artist = ytMusicApi.get_artist(artistBrief['id'])
            totalNewArtists.append(artistBrief['name'])
            
            # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'albums' in artist:
                if 'params' in artist['albums']:
                    albums = ytMusicApi.get_artist_albums(artist['channelId'], artist['albums']['params'])
                else:
                    albums = artist['albums']['results']
            try: albums
            except NameError:
                albums = []

            # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'singles' in artist:
                if 'params' in artist['singles']:
                    singles = ytMusicApi.get_artist_albums(artist['channelId'], artist['singles']['params'])
                else:
                    singles = artist['singles']['results']
            try: singles
            except NameError:
                singles = []

            # Add to 'updatedArtists' to later create new doc in firestore
            newCheckedDoc = {
                "new": True,
                "artistId": artistBrief['id'],
                "name": artistBrief['name'],
                "checkedAlbums": [album['browseId'] for album in albums],
                "checkedSingles": [single['browseId'] for single in singles]
            }
            updatedArtists.append(newCheckedDoc)

    except Exception as error:
        totalArtistErrors.append(f"{artistBrief['id']} {artistBrief['name']}")
        print("Error occured. Skipping this artist.")


# Print errors
print("\n\n= = = = = = = = = = =\n\n")
if (len(totalArtistErrors) > 0):
    print("Errors with artists:\n")
    for error in totalArtistErrors:
        print("     " + error)
else:
    print("No errors.")
# Print final new artists
print("\n\n= = = = = = = = = = =\n\n")
if (len(totalNewArtists) > 0):
    print(f"{len(totalNewArtists)} new artist{'s' if len(totalNewArtists) > 1 else ''}:\n")
    for newArtist in totalNewArtists:
        print("     " + newArtist)
else:
    print("No new artists.")
print("\n\n= = = = = = = = = = =\n\n")
time.sleep(1)
# Print final new singles and albums
if (len(totalNewSinglesAlbums) > 0):
    print(f"{len(totalNewSinglesAlbums)} new single{'s' if len(totalNewSinglesAlbums) > 1 else ''}/album{'s' if len(totalNewSinglesAlbums) > 1 else ''}:\n")
    for newSingleAlbum in totalNewSinglesAlbums:
        print("     " + newSingleAlbum)
else:
    print("No new songs.")
print("\n\n= = = = = = = = = = =\n\n")
time.sleep(1)


# Add to #ToListen
if (len(albumsSinglesIdList) > 0):
    print('Adding all to "#ToListen"...\n')
    fullBrowseIdList = []
    for albumSingle in albumsSinglesIdList:
        songsList = ytMusicApi.get_album(albumSingle)['tracks']
        for song in songsList:
            fullBrowseIdList.append(song['videoId'])
    ytMusicPlaylists = ytMusicApi.get_library_playlists(limit=100)
    for ytMusicPlaylist in ytMusicPlaylists:
        if (ytMusicPlaylist['title'] == "#ToListen"):
            ytMusicApi.add_playlist_items(
                playlistId=ytMusicPlaylist['playlistId'],
                videoIds=fullBrowseIdList,
                duplicates=True
            )
    print("\n= = = = = = = = = = =\n\n")


# Update Checked in firestore
print('Updating database...\n')
for updatedArtist in updatedArtists:
    # IF id exists on 'updatedArtist' then update existing doc
    try:
        checkedCollection.document(updatedArtist.id).update({
            'checkedAlbums': updatedArtist._data['checkedAlbums'],
            'checkedSingles': updatedArtist._data['checkedSingles']
        })
    # ELSE is new, so create new doc
    except:
        checkedCollection.document().set({
            'name': updatedArtist['name'],
            'artistId': updatedArtist['artistId'],
            'checkedAlbums': updatedArtist['checkedAlbums'],
            'checkedSingles': updatedArtist['checkedSingles']
        })
print("\n= = = = = = = = = = =\n\n")

stopwatchEnd = time.perf_counter()
stopwatchTotalString = time.strftime('%M:%S', time.gmtime(stopwatchEnd - stopwatchStart))

print("All finished! Thank you for waiting patiently you impatient prick.")
print(f"The whole script took {stopwatchTotalString}.")
time.sleep(600)