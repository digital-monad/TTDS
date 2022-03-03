import configparser, os, pickle, pymongo
from pymongo import *

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'

client = pymongo.MongoClient(uri)
song_meta_data_collection = client.ttds.songMetaData

current_path = os.path.dirname(__file__)
file = current_path + os.sep + 'test_song_metadata.pickle' # TODO: Iterate through relevant pickle files for index

with open(file, 'rb') as input_file:
    lyrics_dictionary = pickle.load(input_file)

for line_id in lyrics_dictionary:
    song_object = lyrics_dictionary[line_id]
    line_id = str(line_id)
    song_meta_data_collection.insert_many([
        {
            line_id: song_object
        }
    ])
