class ScoreTracker:
    """
    This is a class for keeping track of top N scores in main memory.
    Use add_score() function to add a score to a document
    Use sort_tracker() to sort the scores
    Use get_top() function to retrieve the best document and score values with limit and skip for pagination
    """

    def __init__(self, tracker={}, max_size=100000):
        self.tracker = tracker
        self.sorted_scores = []
        self.max_size = max_size

    def add_score(self, id, score):
        if id in self.tracker:
            self.tracker[id] += score
        else:
            self.tracker[id] = score            
        return

    def sort_tracker(self):
        self.sorted_scores = list(sorted(self.tracker.items(), key=lambda item: item[1]))

    def get_top(self,n,skip):
        return self.sorted_scores[skip:skip+n]


