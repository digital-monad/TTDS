from sklearn.neighbors import NearestNeighbors
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer
import pickle


def sentimentSearch(text):
    """Performs sentiment search to return similar songs to the sentiment of a free-text query

    Args:
        text (String): Non-preprocessed free-text search query

    Returns:
        [int]: Song ids for the 5 closest matching songs to the query
    """

    with open("sentiment.pickle", "rb") as s: # Open the prebuilt tree for knn
        sentimentTree = pickle.load(s)
        sent = analyzer.polarity_scores(text)['compound'] # Get the sentiment score of the song
        distances, ids = songSentiments.kneighbors(sent)
        return ids
