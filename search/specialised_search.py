""""
    This class has functionality to perform specialised searches on a given index.
    The searches it can perform are - boolean, proximity and phrase search.
"""

from re import S
from preprocess import preprocess
import numpy as np
import pickle
import time

class specialised():

    def __init__(self):
        # self.index = super().getIndex() - Once getIndex() is implemented this should return index in agreed format?

        # Index format
        # term : {
        #     song : {
        #         line : [positions]
        #     }
        # }
        pass

    # For now we pass index as an argument but in future we will assign it to self.index via constructor?
    def phrase_search(self, phrase, index, song = False):
        """Conduct n-term phrase search over index. Returns set of matching document ids

        Args:
            phrase ([String]): List of preprocessed tokens in search query
            index (Dictionary): 2D hierarchichal term posting mapping term to songs to lines
        """
        matchingDocs = set() # Set of all doc ids matching the query
        sequenceMap = {} # Dictionary mapping successive terms in the phrase to their view in the index

        if song:
            # Song level phrase search
            for i in range(len(phrase)):
                # TODO: Handle token not being in index
                posting = {song_id : sum(lines.values(), []) for song_id, lines in index[phrase[i]].items()}# Lines and positions where the term appears
                if i == 0: # This is term 1
                    sequenceMap[i] = posting
                else:
                    sequenceMap[i] = {song_id : listing for song_id, listing in posting.items() if song_id in sequenceMap[i-1]}
            matrixCount = {}
            for song_id in sequenceMap[len(phrase) - 1]:
                matching = False
                # For every common line, build the matrix of term occurences per line
                for i in range(len(phrase)):
                    # Get the line's posting list for that term
                    for position in sequenceMap[i][song_id]:
                        updatedValue = matrixCount.get(position - i, 0) + 1
                        if updatedValue == len(phrase):
                            matchingDocs.add(song_id)
                            matching = True
                            break
                        matrixCount[position - i] = updatedValue
                    if matching:
                        break
        else:
            # Line level phrase search
            for i in range(len(phrase)):
                # TODO: Handle token not being in index
                posting = {line_id : positions for song in index[phrase[i]].values() for line_id, positions in song.items()}# Lines and positions where the term appears
                if i == 0: # This is term 1
                    sequenceMap[i] = posting
                else:
                    sequenceMap[i] = {line_id : listing for line_id, listing in posting.items() if line_id in sequenceMap[i-1]}
            matrixCount = {}
            for line_id in sequenceMap[len(phrase) - 1]:
                matching = False
                # For every common line, build the matrix of term occurences per line
                for i in range(len(phrase)):
                    # Get the line's posting list for that term
                    for position in sequenceMap[i][line_id]:
                        updatedValue = matrixCount.get(position - i, 0) + 1
                        if updatedValue == len(phrase):
                            matchingDocs.add(line_id)
                            matching = True
                            break
                        matrixCount[position - i] = updatedValue
                    if matching:
                        break
        return matchingDocs




    def boolean_search(self, terms, index):
        pass

    def proximity_search(self, terms, proximity, index, song): # Two terms

        assert terms[0] in list(index.keys()) and terms[1] in list(index.keys())

        common_songs = self.intersection(list(index[terms[0]].keys()), list(index[terms[1]].keys()))
        common_song_lines = {}
        results = {}

        for song in common_songs:

            common_lines = self.intersection(list(index[terms[0]][song].keys()), list(index[terms[1]][song].keys()))
            common_song_lines[song] = common_lines

        if song == True:

            for song in common_songs:

                ohyeah = True

                while ohyeah:

                    for line1 in index[terms[0]][song].keys():

                        for line2 in index[terms[1]][song].keys():

                            what = [abs(x-y) for x in index[terms[0]][song][line1] for y in index[terms[1]][song][line2]]

                            if len([x for x in what if x <= proximity]) > 0:
                                results[song] = 1

                                ohyeah = False # Should break to next song!!!

                    ohyeah = False

            return results

        else: # Line search


            for song in common_songs:

                results[song] = []

                for line1 in index[terms[0]][song].keys():

                    if line1 in index[terms[1]][song].keys():

                        proxx = [abs(x-y) for x in index[terms[0]][song][line1] for y in index[terms[1]][song][line1] if abs(x-y) <= proximity]

                    if line1 in list(index[terms[1]][song].keys()) and len(proxx) > 0:

                        results[song].append(line1)

            for song in list(results.keys()):
                if len(results[song]) == 0:
                    del results[song]

            return results

    def intersection(self, lst1, lst2):

        return [x for x in lst1 if x in lst2]

def load_pickle(file_name):
    with open("search/" + file_name + '.pickle', 'rb') as f:
        return pickle.load(f)

# TEST STUFF

index = load_pickle("Test_Lyrics_Eminem_index")
song_metadata = load_pickle("Test_Lyrics_Eminem_song_metadata")
lyric_metadata = load_pickle("Test_Lyrics_Eminem_line_metadata")

query = "ethan skateboard"
phrase = [token for token, pos in preprocess(query)[0]]
print(phrase)
s = specialised()
t1 = time.time()
results = s.proximity_search(phrase, 3, index, song = True)
# print(results)
print(f"Took {time.time() - t1} seconds")

# for line_id in results:
#     print(song_metadata[line_id]['title'])