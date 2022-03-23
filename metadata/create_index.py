import argparse, sys
import pandas as pd
from preprocess import preprocessSongLyrics
from preprocess import preprocessSongLyricsMetadata
import bson
import pickle
import gc
import pyarrow as pa 

class Indexer:

    def __init__(self, csv_file, stopping = False, line_id = 0):
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}
        self.artist = csv_file.split("/")[-1][:-4]
        self.stopping = stopping
        self.current_line_id = 0
        self.lyrics = pd.read_csv(csv_file)

    def pickle(self, file_name):
        gc.collect()
        f = open("line_metadata"+file_name+".pickle",'wb')
        pickle.dump(self.line_metadata, f, protocol=4)
        self.line_metadata = {}

    def processSong(self, song_id, artist, title, album, year, date, url, description, lyrics):
        preprocessed_lyrics_metadata = preprocessSongLyricsMetadata(lyrics)
        # Update song metadata
        song_id = str(song_id)
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
        del preprocessed_lyrics_metadata


    def indexFile(self):
        cols = zip(*[self.lyrics[i] for i in self.lyrics.columns])
        song_no = 0
        for song in cols:
            print(song_no)
            self.processSong(*song)
            song_no += 1
            if song_no % 1000 == 0:
                self.pickle(f"phatboi{song_no // 1000}")
        self.pickle("finalboi")

parser = argparse.ArgumentParser(description='Convert CSV files to term positional inverted index.')
parser.add_argument('--file', type=str, required=True, help='File path to CSV file for parsing')
args = parser.parse_args()
indexer = Indexer(args.file)
indexer.indexFile()