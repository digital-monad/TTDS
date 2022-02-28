"""
The 'search' superclass has the functionality to do tasks like fetching the search index 
& parse queries. This class is currently inherited by the all classes which are used for query ranking &
our specialised query searches - boolean, proximity and phrase search.

"""
from pymongo import MongoClient

class search():

    def __init__(self):
        pass

    # Basic idea - to be changed!
    def getIndex(self):
        #this is basics of how to connect to mongodb
        client = MongoClient('localhost', 27017, username='group37', password='VP7SbToaxRFcmUbd') 
        ttds = client.ttds
        collection = ttds.group37 #index created from here

    # TODO - Assuming this would determine which search we do etc...
    def parseQuery():
        pass