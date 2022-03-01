# This script will ultimately write index pickle file into MongoDB

# This inserts CSV file for SongsMetaData
from bson.binary import Binary
import configparser, json, os, pickle, pymongo
from pymongo import *

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'

client = pymongo.MongoClient(uri)
songs_meta_data_collection = client.ttds.invertedIndex

current_path = os.path.dirname(__file__)
file = current_path + os.sep + 'test_index.pickle' # TODO: Iterate through relevant pickle files for index

with open(file, 'rb') as input_file:
    dictionary = pickle.load(input_file)

my_list = [dictionary]

print(my_list)
songs_meta_data_collection.insert_many(my_list)
