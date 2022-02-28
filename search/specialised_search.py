""""
    This class has functionality to perform specialised searches on a given index. 
    The searches it can perform are - boolean, proximity and phrase search.
"""

from search.search import search 

class specialised(search):

    def __init__(self):
        super().__init__()
        # self.index = super().getIndex() - Once getIndex() is implemented this should return index in agreed format?

    # For now we pass index as an argument but in future we will assign it to self.index via constructor?
    def phrase_search(self, phrase, index):
        pass

    def boolean_search(self, terms, index):
        pass

    def proximity_search(self, terms, proximity, index):
        pass