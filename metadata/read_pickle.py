import pickle
import gzip
with gzip.open("line_metadata.pickle","rb") as ifp:
        d = pickle.load(f)
print(len(d))
