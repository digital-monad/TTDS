from heapq import *
import random
from collections import defaultdict

REMOVED = -1
class ScoreTracker:
    """
        This is a class for keeping track of top N scores in main memory.
        Use add_score() function to add a score to a document
        Use sort_tracker() to sort the scores
        Use get_list() function to a list of the tracked scores
    """
    
    def __init__(self, max_size=100000):
        self.heap = []
        self.tracker = {}  # doc_id -> [score, id_or_REMOVED]

        self.max_size = max_size

    def get_list(self):
        return [(id,score) for score,id in filter(lambda fil_score,fil_id: fil_id is not REMOVED, self.tracker.items())]

    def add_score(self, id, score):
        if id in self.tracker:
            score += self.tracker[id][0]
        if len(self.heap) >= self.max_size and score <= self.heap[0][0]:
            # discarded
            return

        self.__remove_entry_if_exists(id)
        entry = [score, id]
        self.tracker[id] = entry
        heappush(self.heap, entry)
        self.__cleanup()

    def __remove_entry_if_exists(self, id):
        if id in self.tracker:
            # mark the entry as removed
            entry = self.tracker.pop(id)
            entry[1] = REMOVED  # set doc_id to removed, so we know the score is no longer valid.

    def __cleanup(self):
        # attempt to tidy up removed entries, and reduce size to max_size
        while True:
            if len(self.heap) == 0:
                break
            if self.heap[0][1] is REMOVED:
                heappop(self.heap)
                continue
            if len(self.heap) > self.max_size:  # here we know that id is not removed, but we have exceeded the size limit
                score, id = heappop(self.heap)
                del self.tracker[id]
                continue
            break  # nothing was removed, so the cleanup has finished. Exit the loop


