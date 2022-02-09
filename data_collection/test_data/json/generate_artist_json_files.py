# This file is used to search for artists with names starting with 'A'
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup
import requests
import lyricsgenius as lg
import os

# TBC: Client access token placed into `settings.ini`
temporary_client_access_token = 'kmNyv2VqWAyRXKncF7_mayGvml4V7nmpxNXQW4yRq1jQE7Uo5YPOFDjdyeeRr-BT'

# TBC: Analyze timeout and retries attributes
genius = lg.Genius(temporary_client_access_token, 
                   skip_non_songs=True, 
                   excluded_terms=["(Remix)", "(Live)"], 
                   remove_section_headers=True,
                   timeout=60,
                   retries=10)

current_path = os.path.dirname(__file__)
file = os.path.normpath(current_path + os.sep + os.pardir + os.sep + 'albums_text' + os.sep + 'artists_a')

artist_list = list()

# TBC: Read multiple files
with open(file, 'r', encoding='utf-8') as file:
    for line in file:
        artist = line.strip()
        artist_data = genius.search_artist(artist, include_features=True) # TODO: CHANGE THE MAX_SONGS
        
        artist_list.append(artist_data)

genius.save_artists(artists= artist_list, overwrite=True)
