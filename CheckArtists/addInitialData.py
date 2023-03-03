import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Setup
firebase_admin.initialize_app( credentials.Certificate('C:/auth/YTMusicManager/ytMusicFirebaseKey.json') )
db = firestore.client()
lastCheckCollection = db.collection(u'LastChecked')

# Get last checked data and backup
with open('data.txt', encoding='utf-8') as f:
    lastCheckedList = f.read().splitlines()

# Add each record
for record in lastCheckedList:
    elements = record.split('|--|')

    name = elements[0].replace('/', '\\')
    artistId = elements[1]
    lastCheckedAlbum = elements[2]
    lastCheckedSingle = elements[3]

    lastCheckCollection.document().set({
        'name': name,
        'artistId': artistId,
        'lastCheckedAlbum': lastCheckedAlbum,
        'lastCheckedSingle': lastCheckedSingle
    })
        