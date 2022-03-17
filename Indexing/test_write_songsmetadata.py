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
    songs_dictionary = pickle.load(input_file)

for song_id in songs_dictionary:
    song_object = songs_dictionary[song_id]
    song_object['song_id'] = song_id
    song_meta_data_collection.insert_many([
        song_object
    ])
