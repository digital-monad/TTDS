import pandas as pd 
from fast_autocomplete import AutoComplete
import signal
from contextlib import contextmanager

class Query_Completion():
    
    def train(self,path):
        lyrics = pd.read_csv(path)

        lyrics = lyrics['Raw Lyrics']
        
        lines = []
        for song in lyrics:
            if type(song) == str:
                lines += song.split('\n')
        
        words = {}
        
        for line in lines[:100000]:
            words[line] = {}
            
        self.auto_complete = AutoComplete(words=words)
        
        
    def query(self, query):
        
        class TimeoutException(Exception): pass

        # NOTE: SIGALRM not supported for Windows
        # @contextmanager
        # def time_limit(seconds):
        #     def signal_handler(signum, frame):
        #         raise TimeoutException("Timed out!")
        #     signal.signal(signal.SIGALRM, signal_handler)
        #     signal.alarm(seconds)
        #     try:
        #         yield
        #     finally:
        #         signal.alarm(0)
        try:
            # with time_limit(1):
            output = self.auto_complete.search(word=query, max_cost=10, size = 10)
            return [' '.join(x) for x in output]
        except TimeoutException as e:
            print("Timed out!")

