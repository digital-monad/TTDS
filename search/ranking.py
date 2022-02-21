""""" Progress so far assumes that we have a query Q and index I (stored as dictionary to work with!
      We also assume that we can access the index which we are yet to implement as we have not decided
      where and how it will be stored - thinking mongoDB """

"""" Assuming the below index structure:

    term1 : {
        song1 : {
            line0 : [pos1, pos2, pos3]
            line1:  [pos1, pos4]
        },
        song2 : {
            line0 : [pos3, pos7]
            line1:  [pos1]
        },
        ...
    }
         """
""" song_metadata: {
        song1: {
            length: 10,
            genre: pop,
            artist: adele
        },
        song2: {
            length: 10,
            genre: pop,
            artist: adele
        },
        ...
    }
    
    lyric_metadata: {
        line1: {
            length: 10,
            song: song
        },
        line2: {
            length: 10,
            song: song
        },
        ...
    }

"""
import math
from search.search import search # This we overused this word lol

class rank(search):

    def __init__(self):
        super()._init__()

    def BM25(self, query, index, avgdl, type): # Assuming query is preprocesses into tokens
        results_dict = {}
        k1 = 1.5 # Constants
        b = 0.75 # Constants
        if type == "song":
            N = len(song_metadata)
            for term in query: # Iterates each term in query
                term_docs = len(list(index[term].keys())) # Number of songs term appears in
                for song in index[term].keys(): # Iterates each song for this given term
                    term_freq_in_doc = 0
                    for line in index[term][song].keys():
                        term_freq_in_doc += len(index[term][song][line]) # Number of instances of term in given song
                    dl = song_metadata[song]['len']
                    # We are now calculating BM25 for a given term in query for a given song
                    score_term = self.calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                    # We now add this to 'results_dict'
                    if song in results_dict.keys():
                        results_dict[song] += score_term
                    else:
                        results_dict[song] = score_term # First song for the term to appear in!
        elif type == "lyric":
            N = len(lyric_metadata)
            for term in query:  # Iterates each term in query
                term_docs = 0
                for song in index[term].keys():  # Iterates each song for this given term
                    term_docs += len(list(index[term][song].keys())) # Number of lyrics term appears in
                for term in query:
                    for song in index[term].keys():
                        for lyric in index[term][song].keys():
                            term_freq_in_doc = len(index[term][song][lyric])
                            dl = lyric_metadata[lyric]['len']
                            # We are now calculating BM25 for a given term in query for a given song
                            score_term = self.calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                            # We now add this to 'results_dict', which will already contain somevalue if previous term apeared in given song
                            if lyric in results_dict.keys():
                                results_dict[lyric] += score_term
                            else:
                                results_dict[lyric] = score_term  # First song for the term to appear in!
        return results_dict

    def calc_BM25(self, N, term_docs, term_freq_in_doc, k1, b, dl, avgdl):
        third_term = self.K(k1, b, dl, avgdl)
        idf_param = math.log( (N-term_docs+0.5) / (term_docs+0.5) ) # Wikipedia says + 1 before taking log
        next_param = ((k1 + 1) * term_freq_in_doc) / (third_term + term_freq_in_doc)
        return float("{0:.4f}".format(next_param * idf_param))

    def K(self, k1, b, d, avgdl):
        return k1 * ((1-b) + b * (float(d)/float(avgdl)) )

def search(type):
    ranky = rank()
    # this can just be hardcoded somewhere
    if type == "song":
        seen_songs = []
        total_songs = 0
        total_length = 0
        for song in song_metadata.keys():
                if song not in seen_songs:
                    total_songs+=1
                    total_length+=song_metadata[song]['len']
                    seen_songs.append(song)
        avgdl_song = total_length/total_songs
        results = ranky.BM25(["hi"], index, avgdl_song, "song")
    elif type == "lyric":
        seen_lyrics = []
        total_lyrics = 0
        total_length = 0
        for lyric in lyric_metadata.keys():
                if lyric not in seen_lyrics:
                    total_lyrics+=1
                    total_length+=lyric_metadata[lyric]['len']
                    seen_lyrics.append(lyric)
        avgdl_lyric = total_length/total_lyrics
        results = ranky.BM25(["hi"], index, avgdl_lyric, "lyric")
    print(results)

if __name__ == '__main__':
    index = {"hi": {'song1': {0: [1,2,3], 13: [1,2,3]}, 'song2':{3: [1,3], 17: [1,2]}}, "good": {'song1': {1: [2,3], 11: [1,2,3]}, 'song2':{2: [1,2,3], 14: [1,2,4,6,7,8]}}}
    song_metadata = {"song1":{"genre": "pop", "artist": "adele", "len": 13,}, "song2":{"genre": "pop","artist": "adele", "len": 19,}}
    lyric_metadata = {0:{"song": "song1", "len": 8,}, 1:{"song": "song1", "len": 8,}, 11:{"song": "song1", "len": 8,}, 13:{"song": "song1", "len": 8,}, 2:{"song": "song2", "len": 8,}, 3:{"song": "song2", "len": 8,}, 14:{"song": "song2", "len": 8,}, 17:{"song": "song2", "len": 8,} }
    search("lyric")