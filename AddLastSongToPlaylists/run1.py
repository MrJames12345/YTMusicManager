import time;
from ytmusicapi import YTMusic


# Setup
stopwatchStart = time.perf_counter()
ytMusicApi = YTMusic('C:/auth/YTMusicManager/ytMusicApiHeaders.json')


# Get last song from history
outputString = '';
lastSong = ytMusicApi.get_history()[0];
print('Song: "' + lastSong['title'] + '"');


# Get playlists to add to
with open('playlists1.js') as f:
    addToPlaylists = f.readlines();
addToPlaylists = list(filter(lambda playlist: '//' not in playlist, addToPlaylists));
addToPlaylists = [playlist.replace('\n', '') for playlist in addToPlaylists]


# Get YT Music playlists
ytMusicPlaylists = ytMusicApi.get_library_playlists(limit=100);


# Add last song to each selected playlist
for addToPlaylist in addToPlaylists:
   for ytMusicPlaylist in ytMusicPlaylists:
      if (ytMusicPlaylist['title'] == addToPlaylist):
         print('Adding to "' + addToPlaylist + '"');
         ytMusicApi.add_playlist_items(
            playlistId=ytMusicPlaylist['playlistId'],
            videoIds=[lastSong['videoId']]
         );


print("\nAll finished! Thank you for waiting patiently you impatient prick.");
time.sleep(3);