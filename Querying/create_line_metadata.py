import argparse, sys
import pandas as pd
from preprocess import preprocessSongLyrics
from preprocess import preprocessSongLyricsMetadata
import bson
import pickle
import gc

class Indexer:

    def __init__(self, csv_file, stopping = False, line_id = 0):
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}
        self.artist = csv_file.split("/")[-1][:-4]
        self.stopping = stopping
        self.current_line_id = 0
        self.lyrics = pd.read_csv(csv_file)

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
        return self.line_metadata

indexer = Indexer("out.csv")
index = indexer.indexFile()
outfile = open("dump","wb")
pickle.dump(index,outfile)
outfile.close()