import os
import sys
import time
from ytmusicapi import YTMusic
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Setup
ytMusicApi = YTMusic('C:/auth/YTMusicManager/ytMusicApiHeaders.json')
firebase_admin.initialize_app( credentials.Certificate('C:/auth/YTMusicManager/ytMusicFirebaseKey.json') )
db = firestore.client()
lastCheckCollection = db.collection(u'LastChecked')

# Get last checked data and backup
with open('data.txt', encoding='utf-8') as f:
    lastCheckedList = f.read().splitlines()

# Add each record
for record in lastCheckedList:

    artistId = None
    artist = None
    albums = []
    singles = []
    albumsIds = []
    singlesIds = []
    
    elements = record.split('|--|')
    name = elements[0].replace('/', '\\')
    artistId = elements[1]

    print(f"Processing: {name}")

    # Get artist
    artist = ytMusicApi.get_artist(artistId)
    
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

    albumsIds = [album['browseId'] for album in albums]
    singlesIds = [single['browseId'] for single in singles]

    lastCheckCollection.document().set({
        'name': name,
        'artistId': artistId,
        'checkedAlbums': albumsIds,
        'checkedSingles': singlesIds
    })
        