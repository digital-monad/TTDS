from ast import Raise
import os
import sys
import logging
import argparse
import pickle
import configparser
from pymongo import MongoClient
import ast
import pymongo

from preprocess import preprocess

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'
client = MongoClient(uri)

sw_path = os.path.dirname(__file__) + os.sep + "englishST.txt"

sw = []

with open(sw_path) as f:
    for line in f:
        for token in preprocess(line.split('\n')[0]):
            sw.append(token)

index_collection = client.ttds.invertedIndexFinal
song_collection = client.ttds.songMetaData
lyric_collection = client.ttds.lyricMetaData

class DBPopulate:
    def __init__(self, path, inserttype):
        self.dir = path
        self.stored = set()

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
        for data in self.temp:
            
            if data['_id'] in sw:
                print("Stop word skipped : " +str(data['_id']))
                continue 

            if data['_id'] in self.stored:
                try:
                    self.collection.update_one({'_id': data['_id']}, {'$set': data})
                except pymongo.errors.DuplicateKeyError:
                    print("Duplicate key error! " + str(data['_id']))
                    continue
            else:
                try:
                    self.collection.insert_one(data)
                    self.stored.add(data['_id'])
                except pymongo.errors.DuplicateKeyError:
                    try:
                        self.collection.update_one({'_id': data['_id']}, {'$set': data})
                        self.stored.add(data['_id'])
                    except pymongo.errors.DuplicateKeyError:
                        print("DOUBLE duplicate error :( " + str(data['_id']))
                        continue
                        

        self.temp.clear()
        logging.info("DB flushed!")

    def write_to_db(self):
        for path, filename in self.__iterate_dir():
            self.temp = self.__read_pickle(path)
            self.__flush_db()

        asd = DBPopulate("../../../../../../../../disk/scratch/s1827995-indexes/small/", "index")
        asd.write_to_db()

