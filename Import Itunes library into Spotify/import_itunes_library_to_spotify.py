import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from lxml import etree
import configparser

# Set up Spotify authentication
config = configparser.ConfigParser()
config.read('config.ini')
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=config['API_KEYS']['YOUR_SPOTIFY_CLIENT_ID'],
    client_secret=config['API_KEYS']['YOUR_SPOTIFY_CLIENT_SECRET'],
    redirect_uri=config['API_KEYS']['YOUR_SPOTIFY_REDIRECT_URI'],
    scope='playlist-modify-public'
))

# Function to extract playlists and tracks from iTunes XML
def parse_itunes_xml(xml_file):
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"The file {xml_file} does not exist.")

    tree = etree.parse(xml_file)
    root = tree.getroot()

    playlists = {}
    tracks = {}

    # Parse tracks first
    for track in root.xpath(".//dict[key='Tracks']/dict/dict"):
        track_id = track.xpath("key[.='Track ID']/following-sibling::integer[1]/text()")
        track_name = track.xpath("key[.='Name']/following-sibling::string[1]/text()")
        artist_name = track.xpath("key[.='Artist']/following-sibling::string[1]/text()")

        if track_id and track_name:
            track_id = track_id[0]
            track_name = track_name[0]
            artist_name = artist_name[0] if artist_name else "Unknown Artist"

            print(f"Track ID: {track_id}")
            print(f"Track Name: {track_name}")
            print(f"Artist Name: {artist_name}")

            tracks[track_id] = (track_name, artist_name)

    # Parse playlists
    for playlist in root.xpath(".//dict[key='Playlists']/array/dict"):
        playlist_name = playlist.xpath("key[.='Name']/following-sibling::string[1]/text()")
        if playlist_name:
            playlist_name = playlist_name[0]
            playlist_items = playlist.xpath(".//array[preceding-sibling::key[1][text()='Playlist Items']]/dict")

            playlists[playlist_name] = []
            for item in playlist_items:
                track_id = item.xpath("integer[1]/text()")
                if track_id:
                    track_id = track_id[0]
                    if track_id in tracks:
                        playlists[playlist_name].append(track_id)

    return playlists, tracks

def create_spotify_playlists(xml_file):
    playlists, tracks = parse_itunes_xml(xml_file)
    print(f"Found {len(playlists)} playlists and {len(tracks)} tracks in the library.")
    created_playlists = {}
    unfound_tracks = {}

    for playlist_name, track_ids in playlists.items():

        # if playlist_name in ("Library", "Songs", "Music", "Downloaded", "TV Shows", "Movies", "Audiobooks", "Podcasts", "2000s Hits Essentials", "90’s Club Songs"):
        #     continue
        try:
            print(f"\nCreating playlist: {playlist_name} with IDs {track_ids}")
            playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name)
            created_playlists[playlist_name] = playlist['id']

            track_uris = []
            unfound_tracks[playlist_name] = []
            for track_id in track_ids:
                if track_id in tracks:
                    track_name, artist_name = tracks[track_id]
                    try:
                        print(f"Searching for track: {track_name} by {artist_name}")
                        results = sp.search(q=f"track:{track_name} artist:{artist_name}", type='track', limit=1)
                        if results['tracks']['items']:
                            track_uri = results['tracks']['items'][0]['uri']
                            track_uris.append(track_uri)
                            print(f"Found track: {track_name} (URI: {track_uri})")
                        else:
                            print(f"Could not find track: {track_name} by {artist_name}")
                            unfound_tracks[playlist_name].append(f"{track_name} by {artist_name}")
                    except Exception as e:
                        print(f"Error searching for track {track_name}: {str(e)}")
                        unfound_tracks[playlist_name].append(f"{track_name} by {artist_name}")

            if track_uris:
                print(f"Adding {len(track_uris)} tracks to playlist {playlist_name}")
                for i in range(0, len(track_uris), 100):  # Spotify allows max 100 tracks per request
                    batch = track_uris[i:i+100]
                    try:
                        sp.playlist_add_items(playlist['id'], batch)
                        print(f"Added batch of {len(batch)} tracks to playlist")
                    except Exception as e:
                        print(f"Error adding tracks to playlist: {str(e)}")
            else:
                print(f"No tracks found for playlist: {playlist_name}")
        except Exception as e:
            print(f"Error creating playlist {playlist_name}: {str(e)}")

    return created_playlists, unfound_tracks

# Path to your iTunes Library XML file
itunes_xml_path = r"itunes_library.xml"

print(f"Using iTunes XML file at: {itunes_xml_path}")

# Create playlists on Spotify
created_playlists, unfound_tracks = create_spotify_playlists(itunes_xml_path)

print("Playlists have been successfully imported to Spotify.")

# Print unfound tracks for each playlist
print("\nUnfound tracks per playlist:")
for playlist, tracks in unfound_tracks.items():
    if tracks:
        print(f"\n{playlist}:")
        for track in tracks:
            print(f"  - {track}")
    else:
        print(f"\n{playlist}: All tracks found")

print("\nImport process completed.")
