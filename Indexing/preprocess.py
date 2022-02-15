
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

        preprocessedSongLyrics[song] = preprocessSongLyrics(songs[song], stopping, stemming)

    return preprocessedSongLyrics

def preprocessSongLyrics(songLyrics,stopping=False,stemming=True):

    """
    Takes a string of lyrics line seperated by \n 

    Returns a 2D array of each line where each element array represents 
    the preprocessed word and it's overall position for that line
    
    """

    preprocessedLines = []

    pos = 0
    
    for line in songLyrics.split("\n"):
        
        tokens = re.sub("\W+", " ",line)

        caseTokens = tokens.casefold().split()

        stemmedLineTokens = []

        for word in caseTokens:
            if (word not in sw or not stopping):
                if stemming:
                    stemmedLineTokens.append((stem(word),pos)) 
                else:
                    stemmedLineTokens.append((word,pos)) 
                pos += 1
        
        if len(stemmedLineTokens) > 0:
            preprocessedLines.append(stemmedLineTokens)
    
    return preprocessedLines

test_lyrics = "22 Lyrics\nIt feels like a perfect night\nTo dress up like hipsters\nAnd make fun of our exes, uh-uh, uh-uh\nIt feels like a perfect night\nFor breakfast at midnight\nTo fall in love with strangers, uh-uh, uh-uh\n\nYeah\nWe're happy, free, confused, and lonely at the same time\nIt's miserable and magical, oh, yeah\nTonight's the night when we forget about the deadlines\nIt's time, oh-oh\n\nI don't know about you, but I'm feeling 22\nEverything will be alright if you keep me next to you\nYou don't know about me, but I'll bet you want to\nEverything will be alright if we just keep dancing like we're\n22, 22\n\nIt seems like one of those nights\nThis place is too crowded\nToo many cool kids, uh-uh, uh-uh\n(Who's Taylor Swift, anyway? Ew)\nIt seems like one of those nights\nWe ditch the whole scene\nAnd end up dreaming\nInstead of sleeping\nYeah\nWe're happy, free, confused, and lonely in the best way\nIt's miserable and magical, oh, yeah\nTonight's the night when we forget about the heartbreaks\nIt's time, oh-oh\n\n(Hey!)\nI don't know about you, but I'm feeling 22\nEverything will be alright (Ooh) if you keep me next to you\nYou don't know about me, but I'll bet you want to\nEverything will be alright if (Alright)\nWe just keep dancing like we're 22 (Oh, oh, oh, oh, oh)\n22 (I don't know about you)\n22, 22\n\nIt feels like one of those nights\nWe ditch the whole scene\nIt feels like one of those nights\nWe won't be sleeping\nIt feels like one of those nights\nYou look like bad news\nI gotta have you\nI gotta have you\nOoh, ooh, yeah\n(Hey!)\nI don't know about you, but I'm feeling 22\nEverything will be alright if (Ooh) you keep me next to you\nYou don't know about me, but I'll bet you want to\nEverything will be alright if we just keep dancing like we're\n22 (Whoa, oh)\n22 (Dancing like)\n22 (Yeah, yeah), 22, (Yeah, yeah, yeah)\n\nIt feels like one of those nights\nWe ditch the whole scene\nIt feels like one of those nights\nWe won't be sleeping\nIt feels like one of those nights\nYou look like bad news\nI gotta have you\nI gotta have you85Embed"
for i in preprocessSongLyrics(test_lyrics):
    print(i)