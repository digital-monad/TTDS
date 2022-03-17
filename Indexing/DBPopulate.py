from ast import Raise
import os 
import sys
import logging
import argparse
import pickle
import configparser
from pymongo import MongoClient
import ast

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'
client = MongoClient(uri)

index_collection = client.ttds.invertedIndex
song_collection = client.ttds.songMetaData
lyric_collection = client.ttds.lyricMetaData

class DBPopulate:
    def __init__(self, path, inserttype):
        self.dir = path

        if inserttype == 'index':
            self.collection = index_collection
        elif inserttype == 'song':
            self.collection = song_collection
        elif inserttype == 'lyric':
            self.collection = lyric_collection
        else:
            raise BaseException("Type not valid!")
        
#        self.temp = dict()

    def __iterate_dir(self):
        """ It itertes all of the leaf files under the root path directory.
        
        Yields:
            string -- leaf path
        """
        for file in os.listdir(self.dir):
            filename = os.fsdecode(file)
            if filename.endswith(".pickle"): 
                yield os.path.join(self.dir, filename), filename

    def __read_pickle(self, path):
        logging.info(path + ' is processing...')
        with open(path, 'rb') as handle:
            file = pickle.load(handle)
        return file

    def __flush_db(self):
        logging.info('DB flushing...')
        print("Processing...")
        self.collection.insert_many(self.temp)
        self.temp.clear()
        logging.info("DB flushed!")

    def write_to_db(self):
        for path, filename in self.__iterate_dir():
            self.temp = self.__read_pickle(path)
            self.__flush_db()

asd = DBPopulate("../../../../../../../../disk/scratch/s1827995-indexes/","index")
asd.write_to_db()
