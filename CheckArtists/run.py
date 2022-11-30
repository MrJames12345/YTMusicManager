from .. import utils;
import time;


# Setup
api = utils.setup();


# Add each artist from 'CheckArtists.txt' to list of objects of [name, lastAlbumId, lastSingleId]
with open('data.txt') as f:
    artists = f.readlines();


# For each artist
for artistLine in artists:

    # Get name, last album id and last single id
    artistElements = artistLine.split('|--|');
    artistName = artistElements[0];
    lastAlbumId = artistElements[1];
    lastSingleId = artistElements[2];

    # Get artist
    artist = getArtist(artistName)

    # Get all albums (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
    if 'albums' in artist:
        if 'params' in artist['albums']:
            albums = api.get_artist_albums(artist['channelId'], artist['albums']['params']);
        else:
            albums = artist['albums']['results'];
    try: albums
    except NameError:
        albums = [];
        print("Artist does not have any albums.");

    # Get all singles (IF 'params' in 'singles', means more than just on first page, so get rest, ELSE use list already retrieved)
    if 'singles' in artist:
        if 'params' in artist['singles']:
            singles = api.get_artist_albums(artist['channelId'], artist['singles']['params']);
        else:
            singles = artist['singles']['results'];
    try: singles
    except NameError:
        singles = [];
        print("Artist does not have any singles.");

    # Make list of all albums up until last checked album
    newAlbums = [];
    for album in albums:
        if album['browseId'] == lastAlbumId:
            break;
        else:
            newAlbums.append(album);

    # Make list of all singles up until last checked album
    newSingles = [];
    for single in singles:
        if single['browseId'] == lastSingleId:
            break;
        else:
            newSingles.append(single);

    # Add all new albums and singles to #ToListen
    fullBrowseIdList = [];
    for album in newAlbums:
        albumSongs = api.get_album(album['browseId'])['tracks'];
        for song in albumSongs:
            fullBrowseIdList.append(song['videoId']);
    for single in newSingles:
        singleSongs = api.get_single(single['browseId'])['tracks'];
        for song in singleSongs:
            fullBrowseIdList.append(song['videoId']);