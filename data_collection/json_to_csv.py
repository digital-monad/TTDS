from os import listdir
from os.path import isfile, join

import csv, json, os, unidecode, re
import configparser

def remove_lyrics_by_section(lyrics):
    '''
        Removes the lyrics by section
        Handles two cases, when lyrics are the following example strings:
            1) "Rolling In The Deep Lyrics\nThere's a fire..."
            2) "Rolling In The Deep LyricsThere's a fire..."
    '''
    first_index = lyrics.find('Lyrics')
    first_index = first_index + len('Lyrics') - 1
    if lyrics[first_index] == '\n':
        skip = 2
    else:
        skip = 1
    cleanedLyrics = lyrics[first_index+skip:].lstrip()
    return cleanedLyrics

def remove_embed(lyrics):
    '''
        Removes the embed problem at the end of lyrics
        The {0,5} in regex is used instead of * to handle infinite loop problem
    '''
    regex = "([0-9]+){0,5}Embed" 
    cleanedLyrics = re.sub(regex, '', lyrics)
    return cleanedLyrics

# Initialize configurations
# config = configparser.ConfigParser()
# current_path = os.path.dirname(__file__)

# All the folders of JSON data should be stored in test_data/json/allJSONs
current_path = os.path.dirname(__file__)
starting_point = os.path.normpath(
    current_path + os.sep + 'test_data' + os.sep + 
    'json' + os.sep + 'allJSONs'
)

song_id = 1
# Go through all the alphabets
for folder in os.listdir(starting_point):
    if folder != '.DS_Store':
        jsonsFolder = starting_point + os.sep + folder
        count = 0

        # Go through all the jsons in current alphabet
        for index, file in enumerate(os.listdir(jsonsFolder), start=0):
            file_path_name = os.path.normpath(jsonsFolder + os.sep + file)

            with open(file_path_name, encoding='utf-8') as json_file:
                json_data = json.load(json_file)

            csv_file = 'artists_' + folder + '.csv'
            json_to_csv_file = os.path.normpath(
                current_path + os.sep + 'test_data' + os.sep + 'csv' + os.sep + csv_file)

            if index == 0:
                read_mode = 'w'
            else:
                read_mode = 'a'

            with open(json_to_csv_file, read_mode, newline='', encoding='utf-8') as data_file:

                csv_writer = csv.writer(data_file)

                for song_data in json_data['songs']:
                    
                    if count == 0:
                        header = ['Song ID','Artist','Title','Album','Year','Date','Image Url','Description','Raw Lyrics']
                        csv_writer.writerow(header)
                        count += 1

                    artist = unidecode.unidecode(json_data['name'])
                    title = unidecode.unidecode(song_data['title'])
                    if song_data.get('album') == None:
                        album = None
                    else:
                        album = song_data.get('album').get('name', None)
                        album = unidecode.unidecode(album)
                    release_date = song_data.get('release_date', None)
                    if release_date == None:
                        year = None
                    else:
                        year = release_date.split("-")[0]
                    song_image_url = song_data['song_art_image_thumbnail_url']
                    if (song_data['description']['plain'].startswith('http') or song_data['description']['plain'] == '?'):
                        song_description = None
                    else:
                        song_description = unidecode.unidecode(song_data['description']['plain'])

                    raw_lyrics = song_data['lyrics']

                    # Filter lyrics that are empty
                    if len(raw_lyrics) > 0:

                        raw_lyrics = remove_lyrics_by_section(raw_lyrics)
                        decoded_raw_lyrics = unidecode.unidecode(raw_lyrics)
                        decoded_raw_lyrics = remove_embed(decoded_raw_lyrics)

                        # Data Cleaning
                        filter1 = len(decoded_raw_lyrics) <= 20000 # Lyrics that are too long may be a play instead of a song
                        filter2 = 'lyrics for this song has yet to be released' not in decoded_raw_lyrics.lower()
                        filter3 = 'song is not released' not in decoded_raw_lyrics.lower()
                        filter4 = 'lyrics for this song have yet to be transcribed' not in decoded_raw_lyrics.lower()                
                        if filter1 and filter2 and filter3 and filter4:
                            csv_writer.writerow([song_id, artist, title, album, year, release_date, song_image_url, song_description, decoded_raw_lyrics])
                            song_id += 1
                        count += 1