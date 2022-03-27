import re, os
from stemming.porter2 import stem

sw_path = os.path.dirname(__file__) + os.sep + "englishST.txt"

sw = []

with open(sw_path) as f:
    for line in f:
        sw.append(line.split('\n')[0])

def preprocessMultipleSongLyrics(songs, stopping=False,stemming=True):

    """
    This takes a dictionary of format {<songname> : <lyrics>}

    Returns a dictonary of format {<songname> : <preprocessed lyrics>}
    
    """
    preprocessedSongLyrics = {}

    for song in songs.keys():

        songLines = preprocessSongLyrics(songs[song], stopping, stemming)

        if(len(songLines)):
            preprocessedSongLyrics[song] = songLines

    return preprocessedSongLyrics

def preprocessSongLyrics(songLyrics,stopping=False,stemming=True):

    """
    Takes a string of lyrics line seperated by \n 

    Returns a 2D array of each line where each element array represents 
    the preprocessed word and it's overall position in the song for that line
    
    """

    preprocessedLines = []

    pos = 0

    for line in songLyrics.split("\n"):

        stemmedLineTokens, pos = preprocess(line, pos, stopping, stemming)

        if len(stemmedLineTokens) > 0:
            preprocessedLines.append(stemmedLineTokens)

    return preprocessedLines

def preprocessSongLyricsMetadata(songLyrics,stopping=False,stemming=False):

    """
    Takes a string of lyrics line seperated by \n

    Returns a 2D array of each line where each element array represents
    the preprocessed word and it's overall position in the song for that line

    """

    preprocessedLines = []

    pos = 0

    for line in songLyrics.split("\n"):

        stemmedLineTokens, pos = preprocessMetadata(line, pos, stopping, stemming)

        if len(stemmedLineTokens) > 0:
            preprocessedLines.append(stemmedLineTokens)

    return preprocessedLines

def preprocessMetadata(sentence, pos=0, stopping=False, stemming=False):

    """ 
    Used for preprocessing a line of text
    """

    tokens = re.sub("\W+", " ",sentence)

    caseTokens = tokens.split()


    stemmedLineTokens = []

    for word in caseTokens:
        word = str(word)
        if (word not in sw or not stopping):
            if stemming:
                stemmedLineTokens.append((str(stem(word)),pos))
            else:
                stemmedLineTokens.append((word,pos))
            pos += 1

    return stemmedLineTokens, pos

def preprocess(sentence, pos=0, stopping=False, stemming=True):

    """ 
    Used for preprocessing a line of text
    """

    tokens = re.sub("\W+", " ",sentence)

    caseTokens = tokens.casefold().split()


    stemmedLineTokens = []

    for word in caseTokens:
        word = str(word)
        if (word not in sw or not stopping):
            if stemming:
                stemmedLineTokens.append((str(stem(word)),pos))
            else:
                stemmedLineTokens.append((word,pos))
            pos += 1

    return stemmedLineTokens, pos

