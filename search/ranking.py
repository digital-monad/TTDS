""""" Progress so far assumes that we have a query Q and index I (stored as dictionary to work with!
      We also assume that we can access the index which we are yet to implement as we have not decided
      where and how it will be stored - thinking mongoDB """

"""" Assuming the below index structure:

    term1 : {
        song1 : {
            [(line0, pos2), (line0, pos13), (line12, pos0)]
        },
        song2 : {
            [(line3, pos5), (line10, pos3)]
            }
        }
        
         """

# Create results dict -> {song : score}
# For term in query 
import math
from numpy import average
import pymongo
from pymongo import MongoClient

#this is how to connect
#should be located in separate MongoDB class file
#index created from here
client = MongoClient('localhost', 27017, username='group37', password='VP7SbToaxRFcmUbd')
ttds = client.ttds
collection = ttds.group37

class rank():

    def __init__(self):
        pass

    def BM25(self, query, index, avgdl): # Assuming query is preprocesses into tokens
        results_dict = {}
        k1 = 1.5 # Constants
        b = 0.75 # Constants
        N = len(index)

        for term in query: # Itterates each term in query 

            term_docs = len(list(index[term].keys())) # Number of songs term apears in

            for song in index[term].keys(): # Itterates each song for this given term 

                term_freq_in_doc = len(index[term][song]) # Number of instances of term in given song
                dl = index[term][song]['len']

                # We are now calculating BM25 for a given term in query for a given song
                score_term = self.calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)

                # We now add this to 'results_dict', which will already contain somevalue if previous term apeared in given song
                if song in results_dict.keys():
                    results_dict[song]+=score_term
                else:
                    results_dict[song] = score_term # First song for the term to apear in!
        return results_dict

    def calc_BM25(self, N, term_docs, term_freq_in_doc, k1, b, dl, avgdl):
        third_term = self.K(k1, b, dl, avgdl)
        idf_param = math.log( (N-term_docs+0.5) / (term_docs+0.5) ) # Wikipedia says + 1 before taking log
        next_param = ((k1 + 1) * term_freq_in_doc) / (third_term + term_freq_in_doc)
        return float("{0:.4f}".format(next_param * idf_param))

    def K(self, k1, b, d, avgdl):
        return k1 * ((1-b) + b * (float(d)/float(avgdl)) )

def main():
    index = {"hi": {'song1': {'len':8, 'pos':[1,2,3]}, 'song2': {'len':6, 'pos':[1,2,3]}}, "bye": {'song1': {'len':8, 'pos':[4,5,6]}, 'song2': {'len':6, 'pos':[4,5,6]}},
             "good": {'song1': {'len':8, 'pos':[7,8]}, 'song3': {'len':4, 'pos':[1,2,3,4]}}, "bad": {'song4': {'len':5, 'pos':[1,2,3,4,5]}},
             "yes": {'song5': {'len':9, 'pos':[1,2,3,4,5,6,7,8,9]}}}
    #this can probs be hardcoded somewhere
    seen_songs = []
    total_songs = 0
    total_length = 0
    for term in index:
        for song in index[term].keys():
            if song not in seen_songs:
                total_songs+=1
                total_length+=index[term][song]['len']
                seen_songs.append(song)
    avgdl = total_length/total_songs
    ranky = rank()
    results = ranky.BM25(["good","bad"], index, avgdl)
    print(results)

if __name__ == '__main__':
    main()