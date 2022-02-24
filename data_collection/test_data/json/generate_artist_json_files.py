# This file is used to search for artists with names starting with 'A'
import configparser, lyricsgenius as lg
import os

current_path = os.path.dirname(__file__)
settings_file = os.path.normpath(
    current_path + os.sep + os.pardir + os.sep + os.pardir + os.sep + os.pardir + os.sep + 'settings.ini'
)
config = configparser.ConfigParser()

config.read(settings_file)

# TBC: Client access token placed into `settings.ini`
genius_lyrics_client_access_token = config.get('geniuslyrics', 'genius_client_access_token')

# TBC: Analyze timeout and retries attributes
genius = lg.Genius(genius_lyrics_client_access_token, 
                   skip_non_songs=True, 
                   excluded_terms=["(Remix)", "(Live)"], 
                   remove_section_headers=True,
                   timeout=600,
                   retries=10)

artist_starting_initial_name = config.get('geniuslyrics_artists_name_letter', 'artist_name_letter')

file = os.path.normpath(current_path + os.sep + os.pardir + os.sep + 'albums_text' + os.sep + artist_starting_initial_name)

artist_list = list()

# Used for now
with open(file, 'r', encoding='utf-8') as file:
    for line in file:
        artist = line.strip()
        artist_data = genius.search_artist(artist, include_features=True) # TODO: CHANGE THE MAX_SONGS

        artist_data.save_lyrics()


# TBC: Used later when problems fixed - Read multiple files
def save_multiple_artists():
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            artist = line.strip()
            artist_data = genius.search_artist(artist, include_features=True) # TODO: CHANGE THE MAX_SONGS
            
            artist_list.append(artist_data)

    genius.save_artists(artists= artist_list, overwrite=True)