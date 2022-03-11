import json
# from lib2to3.pytree import _Results
import pickle
import math
import time
from tracker import ScoreHeap
# from specialised_search import specialised

N = 5
batch_size = 20

def load_json(path):
    return json.load(open(path))

def load_pickle(file_name):
    with open(file_name + '.pickle', 'rb') as f:
        return pickle.load(f)

def idf(term_docs):
    df = len(term_docs)
    if df == 0:
        return 0
    return math.log10(N / df)

def BM25(query, avgdl, type): # Assuming query is preprocesses into tokens
    tracky_track = ScoreHeap()
    results_dict = {}
    k1 = 1.5 # Constants
    b = 0.75 # Constants
    if type == "song":
        N = len(song_metadata)
        for term in query: # Iterates each term in query
            term_docs = len(list(index[term].keys())) # Number of songs term appears in
            if term_docs>0:
                for song in index[term].keys(): # Iterates each song for this given term
                    term_freq_in_doc = 0
                    for line in index[term][song].keys():
                        term_freq_in_doc += len(index[term][song][line]) # Number of instances of term in given song
                    dl = song_metadata[song]['length']
                    # We are now calculating BM25 for a given term in query for a given song
                    score_term = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                    # We now add this to 'results_dict'
                    if song in results_dict.keys():
                        results_dict[song] += score_term
                        tracky_track.add(song, score_term)
                    else:
                        results_dict[song] = score_term # First song for the term to appear in!
                        tracky_track.add(song, score_term)
    elif type == "lyric":
        N = len(lyric_metadata)
        for term in query:  # Iterates each term in query
            term_docs = 0
            if term in index:
                for song in index[term].keys():  # Iterates each song for this given term
                    term_docs += len(list(index[term][song].keys())) # Number of lyrics term appears ins
                for song in index[term].keys():
                    for lyric in index[term][song].keys():
                        term_freq_in_doc = len(index[term][song][lyric])
                        dl = lyric_metadata[lyric]['length']
                        # We are now calculating BM25 for a given term in query for a given song
                        score_term = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                        # We now add this to 'results_dict', which will already contain somevalue if previous term apeared in given song
                        if lyric in results_dict.keys():
                            results_dict[lyric] += score_term
                            tracky_track.add(lyric, score_term)
                        else:
                            results_dict[lyric] = score_term  # First song for the term to appear in!
                            tracky_track.add(lyric, score_term)
    return tracky_track

def calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl):
    third_term = K(k1, b, dl, avgdl)
    idf_param = math.log( (N-term_docs+0.5) / (term_docs+0.5) ) # Wikipedia says + 1 before taking log
    next_param = ((k1 + 1) * term_freq_in_doc) / (third_term + term_freq_in_doc)
    return float("{0:.4f}".format(next_param * idf_param))

def K( k1, b, d, avgdl):
    return k1 * ((1-b) + b * (float(d)/float(avgdl)) )

def ranked_retrieval(query, type, show_results):
    results = BM25(query, batch_size,type)
    result_ids = [item[0] for item in results.getTopN(show_results)]
    return result_ids

if __name__ == '__main__':
    batch_size = 50
    # comment this out if youve got pickle files
    index = load_pickle("Test_Lyrics_Eminem_index")
    song_metadata = load_pickle("Test_Lyrics_Eminem_song_metadata")
    lyric_metadata = load_pickle("Test_Lyrics_Eminem_line_metadata")
    start = time.time()
    # uncomment this if you havent got pickle files
    # index = {"hi": {'song1': {0: [1,2,3], 13: [1,2,3]}, 'song2':{1:[1]}}, "good": {'song1': {1: [2,3], 11: [1,2,3]}, 'song2':{2: [1,2,3], 14: [1,2,4,6,7,8]}}}
    # song_metadata = {"song1":{"genre": "pop", "artist": "adele", "len": 13,}, "song2":{"genre": "pop","artist": "adele", "len": 19,}}
    # lyric_metadata = {0:{"song": "song1", "len": 8,}, 1:{"song": "song1", "len": 8,}, 11:{"song": "song1", "len": 8,}, 13:{"song": "song1", "len": 8,}, 2:{"song": "song2", "len": 8,}, 3:{"song": "song2", "len": 8,}, 14:{"song": "song2", "len": 8,}, 17:{"song": "song2", "len": 8,} }
    
    tracker = ranked_retrieval(['chorus','hurt','pain'], 'song', batch_size)
    tracker = ranked_retrieval(['hurt'], 'lyric', batch_size)
    print(len(tracker))
    end = time.time()
    print(f'''Run time = {end-start}''')
    print(f'''Results = {tracker}''')


