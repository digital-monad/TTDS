# File batching with multiple JSON files for each artist initial name to one singular CSV file

from os import listdir
from os.path import isfile, join

import csv, json, os, unidecode
import configparser

# Initialize configurations
config = configparser.ConfigParser()
current_path = os.path.dirname(__file__)

config.read('settings.ini') # Configuration settings file may be placed elsewhere
data_collection_type = config.get('geniuslyrics_data_collection', 'data_collection_type')
batch_starting_initial = config.get('geniuslyrics_data_collection', 'batch_starting_initial')

batch_starting_initial_folder = os.path.normpath(
    current_path + os.sep + data_collection_type + os.sep + 
    'json' + os.sep + batch_starting_initial
)

relevant_files = [f for f in listdir(batch_starting_initial_folder) if isfile(join(batch_starting_initial_folder, f))]

count = 0 # Counter variable used for writing headers to CSV file

for index, file in enumerate(relevant_files, start=0):

    file_path_name = os.path.normpath(batch_starting_initial_folder + os.sep + file)

    with open(file_path_name, encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    
    csv_file = 'artists_' + batch_starting_initial + '.csv'

    json_to_csv_file = os.path.normpath(
        current_path + os.sep + data_collection_type + os.sep +
        'csv' + os.sep + csv_file)

    if index == 0:
        read_mode = 'w'
    else:
        read_mode = 'a'

    with open(json_to_csv_file, read_mode, newline='', encoding='utf-8') as data_file:

        csv_writer = csv.writer(data_file)

        for song_data in json_data['songs']:
            
            if count == 0:
                header = ['Song ID','Artist','Title','Album', 'Year', 'Date','Raw Lyrics']
                csv_writer.writerow(header)
                count += 1

            song_id = count
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
            raw_lyrics = song_data['lyrics']
            first_index = raw_lyrics.find('\n') # Remove 'lyrics by... section'
            raw_lyrics = raw_lyrics[first_index+1:]

            decoded_raw_lyrics = unidecode.unidecode(raw_lyrics)

            if len(decoded_raw_lyrics) <= 20000:
                csv_writer.writerow([song_id, artist, title, album, year, release_date, decoded_raw_lyrics])
            
            count += 1