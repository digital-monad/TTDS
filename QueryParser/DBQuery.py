from typing import List
from pymongo import MongoClient
import json
import re
from operator import itemgetter

class DBQuery():

    def __init__(self):
        super().__init__()
        client = MongoClient('mongodb+srv://group37:VP7SbToaxRFcmUbd@ttds-group-37.0n876.mongodb.net/test')
        self.ttds = client.ttds
        self.inverted_index = self.ttds.invertedIndex
        self.lyricMetaData = self.ttds.lyricMetaData
        self.songMetaData = self.ttds.songMetaData    
            
    def get_indexed_by_terms(self, terms):
        return self.inverted_index.find({"$or":[{"_id":term} for term in terms]}) 

    def countSongs(self):
        return self.songMetaData.estimated_document_count()
        
    def countLyrics(self):
        return self.lyricMetaData.estimated_document_count()


x = DBQuery()

for res in x.get_indexed_by_terms(['bean']):
    print(res)

# print(x.countLyrics())
# print(len(list(x.lyricMetaData.find())))
# print(x.countSongs())
# print(len(list(x.songMetaData.find())))

# for res in results.skip(1):
#     print(res)