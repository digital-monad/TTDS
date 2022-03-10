from pymongo import MongoClient
from preprocess import preprocess

class Search():

    def __init__(self):
        """Connects to MongoDB
        """
        client = MongoClient('localhost', 27017, username='group37', password='VP7SbToaxRFcmUbd')
        ttds = client.ttds
        self.collection = ttds.invertedIndex

    def queryIndex(self, terms):
        """Pull results from the index

        Args:
            terms ([String]): List of preprocessed tokens to query the index with
        """
        # TODO: Parse returned results into numba typed dict
        return self.collection.find({"key" : {"in" : terms}})

    def preprocessQuery(self, query):
        """Preprocess some query text into a list of tokens

        Args:
            query (String): Free query text

        Returns:
            [String]: List of preprocessed tokens
        """
        return preprocess(query)[0]

    def phraseSearch(self, phrase, song):

        """Conduct n-term phrase search over index and return set of matching document ids

        Args:
            phrase (String): Free text search query
            song (Bool): Whether or not to perform song search (rather than lyric search)

        Returns:
            Set[Int]: Document ids of all matching documents
        """


        phrase_terms = self.preprocessQuery(phrase) # Preprocess the text
        index = self.queryIndex(phrase_terms) # Get the index entries for these terms
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

        def proximity_search(self, terms, proximity, song): # Two terms

            terms = self.preprocessQuery(phrase) # Preprocess the text
            index = self.queryIndex(phrase_terms) # Get the index entries for these terms

            assert terms[0] in list(index.keys()) and terms[1] in list(index.keys())

            common_songs = self.intersection(list(index[terms[0]].keys()), list(index[terms[1]].keys()))
            common_song_lines = {}
            results = {}

            for song in common_songs:

                common_lines = self.intersection(list(index[terms[0]][song].keys()), list(index[terms[1]][song].keys()))
                common_song_lines[song] = common_lines

            if song == True:

                print("Why")
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

                print("Surely")

                for song in common_songs:

                    results[song] = []

                    for line1 in index[terms[0]][song].keys():

                        if line1 in index[terms[1]][song].keys():

                            proxx = [abs(x-y) for x in index[terms[0]][song][line1] for y in index[terms[1]][song][line1] if abs(x-y) <= proximity]

                        if line1 in list(index[terms[1]][song].keys()) and len(proxx) > 0:

                            print("Append")
                            results[song].append(line1)

                for song in list(results.keys()):
                    if len(results[song]) == 0:
                        del results[song]

                print("return")
                return results
