import os
import sys
import json
sys.path.append('../')
import utils
import time

stopwatchStart = time.perf_counter()

# Setup
api = utils.setup()

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

# Get last checked data and backup
with open('data.txt', encoding='utf-8') as f:
    lastCheckedList = f.read().splitlines()
i = 0
while os.path.exists(f"backups/data_backup_{i}.txt"):
    i += 1
f = open(f"backups/data_backup_{i}.txt", 'w', encoding='utf-8')
for record in lastCheckedList:
    f.write(record + "\n")
f.close()

# Get all artists from my playlists
artistsToCheck = []
print("\nGetting artists from:\n")
playlistsBrief = api.get_library_playlists(limit=100)
for playlistBrief in playlistsBrief:
    # IF is a playlist to check
    if playlistBrief['title'] in playlistsToAddFrom:
        print("     - " + playlistBrief['title'])
        playlist = api.get_playlist(playlistBrief['playlistId'], limit=None)
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

# Setup albums and singles list to add to #ToListen
albumsSinglesIdList = []
# Setup new artists list to save at end
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
        artistLastChecked = None
        artistElements = None
        artistName = None
        lastAlbumId = None
        lastSingleId = None
        albums = []
        singles = []
        newAlbums = []
        newSingles = []
        albumText = None
        singleText = None

        print("")

        print(f"Checking: {artistBrief['name']}")

        # Get last checked record for artist
        for record in lastCheckedList:
            if record is not None and record.split('|--|')[1] == artistBrief['id']:
                artistLastChecked = record
                break
        
        # IF found record, check artist
        if artistLastChecked is not None:

            artistElements = artistLastChecked.split('|--|')
            lastAlbumId = artistElements[2]
            lastSingleId = artistElements[3]

            # Get artist
            artist = api.get_artist(artistBrief['id'])

            # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'albums' in artist:
                if 'params' in artist['albums']:
                    albums = api.get_artist_albums(artist['channelId'], artist['albums']['params'])
                else:
                    albums = artist['albums']['results']
            try: albums
            except NameError:
                albums = []

            # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'singles' in artist:
                if 'params' in artist['singles']:
                    singles = api.get_artist_albums(artist['channelId'], artist['singles']['params'])
                else:
                    singles = artist['singles']['results']
            try: singles
            except NameError:
                singles = []

            # Get list of all albums up until last checked album
            for album in albums:
                if album['browseId'] == lastAlbumId:
                    break
                else:
                    newAlbums.append(album)

            # Get list of all singles up until last checked album
            for single in singles:
                if single['browseId'] == lastSingleId:
                    break
                else:
                    newSingles.append(single)

            # Add new albums, unless there are too many which means ytmusic changed something that fucked me over
            if (len(newAlbums) > 0 and len(newAlbums) < 5):
                for newAlbum in newAlbums:
                    print("New album: " + newAlbum['title'])
                    albumsSinglesIdList.append(newAlbum['browseId'])
                    totalNewSinglesAlbums.append(artistBrief['name'] + ' - ' + newAlbum['title'] + " (Album)")
            elif (len(newAlbums) > 5):
                print("Too many albums!\nSkipping these albums and resetting this artist's last album id.")

            # Add new singles, unless there are too many which means ytmusic changed something that fucked me over
            if (len(newSingles) > 0 and len(newSingles) < 5):
                for newSingle in newSingles:
                    print("New single: " + newSingle['title'])
                    albumsSinglesIdList.append(newSingle['browseId'])
                    totalNewSinglesAlbums.append(artistBrief['name'] + ' - ' + newSingle['title'] + " (Single)")
            elif (len(newSingles) > 5):
                print("Too many singles!\nSkipping these singles and resetting this artist's last single id.")

        # ELSE is new, so just get latest single and album
        else:

            print("New Artist!")

            # Get artist
            artist = api.get_artist(artistBrief['id'])
            totalNewArtists.append(artistBrief['name'])
            
            # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'albums' in artist:
                if 'params' in artist['albums']:
                    albums = api.get_artist_albums(artist['channelId'], artist['albums']['params'])
                else:
                    albums = artist['albums']['results']
            try: albums
            except NameError:
                albums = []

            # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
            if 'singles' in artist:
                if 'params' in artist['singles']:
                    singles = api.get_artist_albums(artist['channelId'], artist['singles']['params'])
                else:
                    singles = artist['singles']['results']
            try: singles
            except NameError:
                singles = []
                    
        # Add artist to updated artists list
        albumText = "" if len(albums) == 0 else albums[0]['browseId']
        singleText = "" if len(singles) == 0 else singles[0]['browseId']
        updatedArtists.append(artistBrief['name'] + "|--|" + artistBrief['id'] + "|--|" + albumText + "|--|" + singleText)

    except:
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
        songsList = api.get_album(albumSingle)['tracks']
        for song in songsList:
            fullBrowseIdList.append(song['videoId'])
    ytMusicPlaylists = api.get_library_playlists(limit=100)
    for ytMusicPlaylist in ytMusicPlaylists:
        if (ytMusicPlaylist['title'] == "#ToListen"):
            api.add_playlist_items(
                playlistId=ytMusicPlaylist['playlistId'],
                videoIds=fullBrowseIdList,
                duplicates=True
            )
    print("\n= = = = = = = = = = =\n\n")


# Update 'artists.txt'
f = open('data.txt', 'w', encoding='utf-8')
for artist in updatedArtists:
    f.write(artist + "\n")
f.close()

stopwatchEnd = time.perf_counter()
stopwatchTotalString = time.strftime('%M:%S', time.gmtime(stopwatchEnd - stopwatchStart))

print("All finished! Thank you for waiting patiently you impatient prick.")
print(f"The whole script took {stopwatchTotalString}.")
time.sleep(600)