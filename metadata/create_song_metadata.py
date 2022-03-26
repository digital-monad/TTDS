import pickle, argparse, sys
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

# song_id artist title album year date lyrics

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
        with open("song_metadata.pickle", 'wb') as handle:
            pickle.dump([{**{"_id" : id}, **self.song_metadata[id]} for id in self.song_metadata], handle)

    def processSong(self, song_id, artist, title, album, year, date, url, description, lyrics):
        print(f"Processing song {title}")
        preprocessed_lyrics = preprocessSongLyrics(lyrics)
        # Update song metadata
        song_id = str(song_id)
        self.song_metadata[song_id] = {
            "title" : title,
            "artist" : artist,
            "album" : album,
            "year" : year,
            "length" : sum(map(len,preprocessed_lyrics)),
            "image_url" : url,
            "description" : description
        }

    def indexFile(self):
        cols = zip(*[self.lyrics[i] for i in self.lyrics.columns])
        for song in cols:
            self.processSong(*song)
        self.pickle("finalboi")

parser = argparse.ArgumentParser(description='Convert CSV files to term positional inverted index.')
parser.add_argument('--file', type=str, required=True, help='File path to CSV file for parsing')
args = parser.parse_args()
indexer = Indexer(args.file)
indexer.indexFile()


# Run : python create_index.py --file {path to csv} --batch-size {number}
