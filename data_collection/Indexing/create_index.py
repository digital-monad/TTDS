import pickle
import pandas as pd

"""
index = {
    term : {
        song : {
            line_0 : [1,4],
            line_2 : [3]
        }
    }
}
"""

index = {}
song_metadata = {}
line_metadata = {}

def preprocess(text):
    pass

test_file = "Eminiem.csv"
lyrics = pd.read_csv(test_file)

# song_id artist title album year date lyrics

class Indexer:

    def __init__(self, artist, stopping = False):
        self.file = artist + ".csv"
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}
        self.artist = artist
        self.stopping = stopping

    def pickle(self):
        pickle.dumps(self.index, self.artist + "_index_pickle")
        pickle.dumps(self.song_metadata, self.artist + "_song_metadata_pickle")
        pickle.dumps(self.index, self.artist + "_line_metadata_pickle")
    
    def processSong(self, song_id, artist, title, album, year, date, lyrics):
        lyrics = preprocess(lyrics)