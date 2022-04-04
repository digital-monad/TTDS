import argparse, sys
import pandas as pd
from preprocess import preprocessSongLyrics
from preprocess import preprocessSongLyricsMetadata
import bson
import pickle
import gc

class Indexer:

    def __init__(self, stopping = False, line_id = 0):
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}
        self.stopping = stopping
        self.current_line_id = 0
        self.lyrics = pd.read_csv("out.csv")

    def pickle(self, file_name):
        with open("./line/"+file_name+".pickle", "wb") as handle:
            pickle.dump([{**{"_id" : id}, **self.line_metadata[id]} for id in self.line_metadata], handle)
        self.line_metadata = {}

    def processSong(self, song_id, artist, title, album, year, date, url, description, lyrics):
        # Update song metadata
        song_id = str(song_id)
        preprocessed_lyrics_metadata = preprocessSongLyricsMetadata(lyrics)
        for line in preprocessed_lyrics_metadata:
            # Update line metadata
            line_id = self.current_line_id
            line_id = str(line_id)
            self.line_metadata[line_id] = {
                "song_id" : song_id,
                "length" : len(line),
                "text" : " ".join([token for token, pos in line])
            }
            # Increment the line id
            self.current_line_id += 1

    def indexFile(self):
        cols = zip(*[self.lyrics[i] for i in self.lyrics.columns])
        i = 0
        for song in cols:
            print(i)
            print("\n")
            self.processSong(*song)
            i+=1
            if i % 100 == 0:
                print(f"Pickling batch {i}")
                self.pickle(f"phatboi{i}")
        self.pickle("finalboi")

indexer = Indexer("out.csv")
index = indexer.indexFile()
