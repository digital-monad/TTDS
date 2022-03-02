# This script will ultimately write index pickle file into MongoDB

# This inserts CSV file for SongsMetaData
from operator import index
from bson.objectid import ObjectId
import configparser, json, os, pickle, pymongo
from pymongo import *

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'

client = pymongo.MongoClient(uri)
inverted_index_collection = client.ttds.invertedIndex

current_path = os.path.dirname(__file__)
file = current_path + os.sep + 'test_index.pickle' # TODO: Iterate through relevant pickle files for index

with open(file, 'rb') as input_file:
    index_dictionary = pickle.load(input_file)

for key_term in index_dictionary:
    song_id = index_dictionary[key_term]
    inverted_index_collection.insert_many([
        {
            "key": str(key_term),
            key_term: song_id
        }
    ])

inverted_index_collection.create_index('_id')
inverted_index_collection.create_index('key')

meow = list(inverted_index_collection.find({"key": {"$in": ['intro', 'look']}}))
