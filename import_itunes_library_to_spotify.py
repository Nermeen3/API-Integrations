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

# Function to create playlists on Spotify
def create_spotify_playlists(xml_file):
    playlists, tracks = parse_itunes_xml(xml_file)
    created_playlists = {}

    for playlist_name, track_ids in playlists.items():
        if playlist_name in ("Library", "Songs", "Music", "Downloaded", "TV Shows", "Movies", "Audiobooks", "Podcasts"):
            continue
        try:
            playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name)
            created_playlists[playlist_name] = playlist['id']

            track_uris = []
            for track_id in track_ids:
                if track_id in tracks:
                    track_name, artist_name = tracks[track_id]
                    try:
                        results = sp.search(q=f"track:{track_name}", limit=1, type='track')
                        if results['tracks']['items']:
                            track_uris.append(results["tracks"]["items"][0]["uri"])
                        else:
                            print(f"Could not find track: {track_name} by {artist_name}")
                    except Exception as e:
                        print(f"Error searching for track {track_name}: {str(e)}")

            if track_uris:
                sp.playlist_add_items(playlist['id'], track_uris)
            else:
                print(f"No tracks found for playlist: {playlist_name}")
        except Exception as e:
            print(f"Error creating playlist {playlist_name}: {str(e)}")
        break

    return created_playlists

# Path to your iTunes Library XML file
itunes_xml_path = r"D:\\Users\\PC\\PycharmProjects\\Import Itunes to Spotify\\itunes_library.xml"

print(f"Using iTunes XML file at: {itunes_xml_path}")

# Create playlists on Spotify
created_playlists = create_spotify_playlists(itunes_xml_path)

print("Playlists and tracks have been successfully imported to Spotify.")
