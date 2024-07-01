import xml.etree.ElementTree as ET
import json


def parse_itunes_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Verify structure
    plist_dict = root.find('dict')
    if plist_dict is None:
        raise ValueError("The XML does not contain a 'dict' element at the expected location.")

    tracks_dict = None
    playlists_array = None

    for elem in plist_dict:
        if elem.tag == 'key' and elem.text == 'Tracks':
            tracks_dict = elem.find('dict')
        elif elem.tag == 'key' and elem.text == 'Playlists':
            playlists_array = elem.find('array')

    if tracks_dict is None:
        raise ValueError("The XML does not contain a 'Tracks' element.")
    if playlists_array is None:
        raise ValueError("The XML does not contain a 'Playlists' element.")

    playlists = []
    tracks = []

    for plist in playlists_array.findall('dict'):
        playlist = {}
        for item in plist:
            if item.tag == 'key':
                key = item.text
                value = item.findnext().text
                playlist[key] = value
        playlists.append(playlist)

    for track in tracks_dict.findall('dict'):
        track_info = {}
        for item in track:
            if item.tag == 'key':
                key = item.text
                value = item.findnext().text
                track_info[key] = value
        tracks.append(track_info)

    return playlists, tracks


def main(xml_file, output_file):
    playlists, tracks = parse_itunes_xml(xml_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"playlists": playlists, "tracks": tracks}, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    xml_file = r"itunes_library.xml"
    output_file = "output.json"
    main(xml_file, output_file)
