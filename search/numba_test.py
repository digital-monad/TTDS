import pickle
from numba import njit, typed, types, typeof


def load_pickle(file_name):
    with open(file_name + '.pickle', 'rb') as f:
        return pickle.load(f)

index = load_pickle("search/Test_Lyrics_Eminem_index")

print(type(index))

def dict_to_nb(d):
    line2pos = typed.Dict.empty(
        key_type=types.int64, # line id
        value_type=types.ListType(types.int64) # list of positions
    )
    song2pos = typed.Dict.empty(
        key_type=types.int64, # song id
        value_type=typeof(line2pos) # lines and positions dict
    )
    nb_index = typed.Dict.empty(
        key_type=types.unicode_type, # term token
        value_type=typeof(song2pos) # songs and lines dict
    )
    for term in d:
        nb_index[term] = typed.Dict.empty(
        key_type=types.int64, # song id
        value_type=typeof(line2pos) # lines and positions dict
    )
        for song in d[term]:
            nb_index[term][song] = typed.Dict.empty(
                key_type=types.int64, # line id
                value_type=types.ListType(types.int64) # list of positions
            )
            for line in d[term][song]:
                nb_index[term][song][line] = typed.List(d[term][song][line])
    return nb_index
nb_index = dict_to_nb(index)


import numpy as np
@njit
def phraseSearch(phrase, song):

        """Conduct n-term phrase search over index and return set of matching document ids

        Args:
            phrase (String): Free text search query
            song (Bool): Whether or not to perform song search (rather than lyric search)

        Returns:
            Set[Int]: Document ids of all matching documents
        """


        index = nb_index
        matchingDocs = set() # Set of all doc ids matching the query
        sequenceMap = {} # Dictionary mapping successive terms in the phrase to their view in the index

        if song:
            # Song level phrase search
            for i in range(len(phrase)):
                # TODO: Handle token not being in index
                posting = {song_id : np.concatenate(typed.List(lines.values())) for song_id, lines in index[phrase[i]].items()}# Lines and positions where the term appears
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


from preprocess import preprocess
query = "office with monica"
phrase = [token for token, pos in preprocess(query)[0]]
phraseSearch(phrase, False)