import pickle, argparse
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

    def __init__(self, csv_file, batch_size, stopping = False, line_id = 0):
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}
        self.artist = csv_file.split("/")[-1][:-4]
        self.stopping = stopping
        self.batch_size = batch_size
        self.current_line_id = 0
        self.lyrics = pd.read_csv(csv_file)

    def pickle(self, file_name):
        with open(file_name + "_index.pickle", 'wb') as handle:
            pickle.dump(self.index, handle)
        with open(file_name + "_song_metadata.pickle", 'wb') as handle:
            pickle.dump(self.song_metadata, handle)
        with open(file_name + "_line_metadata.pickle", 'wb') as handle:
            pickle.dump(self.line_metadata, handle)
        # Clear memory
        self.index = {}
        self.song_metadata = {}
        self.line_metadata = {}



    def processSong(self, song_id, artist, title, album, year, date, lyrics):
        print(f"Processing song {title}")
        preprocessed_lyrics = preprocessSongLyrics(lyrics)
        # Update song metadata
        self.song_metadata[song_id] = {
            "title" : title,
            "artist" : artist,
            "album" : album,
            "year" : year,
            "length" : sum(map(len,preprocessed_lyrics))
        }
        for line in preprocessed_lyrics:
            # Update line metadata
            line_id = self.current_line_id
            self.line_metadata[line_id] = {
                "song_id" : song_id,
                "length" : len(line),
                "text" : " ".join([token for token, pos in line])
            }
            # Update the index
            for term,pos in line:
                if term not in self.index:
                    self.index[term] = {}
                if song_id not in self.index[term]:
                    self.index[term][song_id] = {}
                if  line_id not in self.index[term][song_id]:
                    self.index[term][song_id][line_id] = []
                self.index[term][song_id][line_id].append(pos)
            # Increment the line id
            self.current_line_id += 1

    def indexFile(self):
        cols = zip(*[self.lyrics[i] for i in self.lyrics.columns])
        for song in range(len(cols)):
            self.processSong(*cols[song])
            if song % self.batch_size == 0:
                self.pickle(f"phatboi{song // self.batch_size}")
        self.pickle("finalboi")

parser = argparse.ArgumentParser(description='Convert CSV files to term positional inverted index.')
parser.add_argument('--file', type=str, required=True, help='File path to CSV file for parsing')
parser.add_argument('--batch-size', type=int, default=10000, help='Size of each pickle file')
args = parser.parse_args()
indexer = Indexer(args.file, args.batch_size)
indexer.indexFile()


# Run : python create_index.py --file {path to csv} --batch-size {number}