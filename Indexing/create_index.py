import pickle
import pandas as pd
from preprocess import preprocessSongLyrics

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

    def __init__(self, artist, stopping = False, line_id = 0):
        lyrics_file = artist + ".csv"
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}
        self.artist = artist
        self.stopping = stopping
        self.current_line_id = 0
        self.lyrics = pd.read_csv(lyrics_file)

    def pickle(self):
        pickle.dumps(self.index, self.artist + "_index_pickle")
        pickle.dumps(self.song_metadata, self.artist + "_song_metadata_pickle")
        pickle.dumps(self.index, self.artist + "_line_metadata_pickle")
    
    def processSong(self, song_id, artist, title, album, year, date, lyrics):
        preprocessed_lyrics = preprocessSongLyrics(lyrics)
        # Update song metadata
        song_metadata[song_id] = {
            "title" : title,
            "artist" : artist,
            "album" : album,
            "year" : year,
            "length" : sum(map(len,preprocessed_lyrics))
        }
        for line in preprocessed_lyrics:
            # Update line metadata
            line_id = self.current_line_id
            line_metadata[line_id] = {
                "song_id" : song_id,
                "length" : len(line)
            }
            # Update the index
            for term,pos in line:
                if term not in index:
                    index[term] = {}
                if song_id not in index[term]:
                    index[term][song_id] = {}
                if  line_id not in index[term][song_id]:
                    index[term][song_id][line_id] = []
                index[term][song_id][line_id].append(pos)
            # Increment the line id
            self.current_line_id += 1
    
    def indexFile(self):
        for song in zip(self.lyrics.columns):
            processSong