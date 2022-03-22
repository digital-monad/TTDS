using PyCall
using BenchmarkTools
using SparseArrays
using DataStructures
using Traceur
using Mongoc
using BSON

py"""
import pickle

def load_pickle(fpath):
    print(fpath)
    with open(fpath, "rb") as f:
        data = pickle.load(f)
    return data
"""

load_pickle = py"load_pickle"

using DataStructures

function add_score(id,score,heap,tracker)
    max_size = 100000
    if id in keys(tracker)
        score += tracker[id]
    end
    if length(heap) >= max_size && score <= tracker[first(heap)]
        # discarded
        return
    end
    __remove_entry_if_exists(heap,tracker, id)
    tracker[id] = score
    push!(heap, id)
    __cleanup(heap, tracker)
end

function __remove_entry_if_exists(heap,tracker, id)
    if id in keys(tracker)
        delete!(tracker, id)
        delete!(heap, id)
    end
end

function __cleanup(heap,tracker)
    max_size = 100000
    while true
        if length(heap) == 0
            break
        end
        if length(heap) > max_size  # here we know that id is not removed, but we have exceeded the size limit
            id = pop!(heap)
            delete!(tracker, id)
            continue
        end
        break  # nothing was removed, so the cleanup has finished. Exit the loop
    end
end

function songQuery(collection, term)
    doc = Mongoc.find_one(collection, Mongoc.BSON("""{ "_id" : "$term" }"""))
end

function BM25(query, search_type,index,song_metadata,lyric_metadata)
    heap = MutableBinaryMinHeap{String}()
    tracker = Dict{String, Float64}()
    k1 = 1.5 # Constants
    b = 0.75 # Constants
    if search_type == "song"
        N = 1307152
        for term in query
            songs = collect(keys(index[term]))
            filter!(e->e∉["song_df","line_df","_id"],songs)
            metadatas = Dict(song => Mongoc.as_dict(songQuery(song_metadata, song)) for song in songs)
            term_docs = length([i for i in keys(index[term])]) - 3
            if term_docs>0
                for song in songs
                    term_freq_in_doc = index[term][song]["tf"]
                    dl = metadatas[song]["length"]
                    avgdl = 1000 #change this
                    score = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                    add_score(song,score,heap,tracker)
                end
            end
        end
    elseif search_type == "lyric"
        N = 60000000
        for term in query  # Iterates each term in query
            term_docs = 0
            if term in keys(index)
                for song in keys(index[term]) # Iterates each song for this given term
                    term_docs += length(keys(index[term][song])) # Number of lyrics term appears ins
                end
            end
            if term_docs>0
                for song in keys(index[term]) # Iterates each song for this given term
                    term_docs += length(keys(index[term][song])) # Number of lyrics term appears ins
                end
                for song in keys(index[term])
                    for lyric in keys(index[term][song])
                        term_freq_in_doc = length(index[term][song][lyric])
                        dl = lyric_metadata[lyric]["length"]
                        # We are now calculating BM25 for a given term in query for a given song
                        avgdl = 10 #change this
                        score_term = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                        # We now add this to 'results_dict', which will already contain somevalue if previous term apeared in given song
                        add_score(lyric,score_term,heap,tracker)
                    end
                end
            end
        end
    end
    #convert this to dataframe
    return tracker
end

function calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
    third_term = k1 * ((1-b) + b * (float(dl)/float(avgdl)))
    idf_param = log( (N-term_docs+0.5) / (term_docs+0.5) ) # Wikipedia says + 1 before taking log
    next_param = ((k1 + 1) * term_freq_in_doc) / (third_term + term_freq_in_doc)
    return round((next_param * idf_param),digits=4)
end

function establishConnection()
    client = Mongoc.Client("mongodb+srv://group37:VP7SbToaxRFcmUbd@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority&tlsCAFile=/usr/local/etc/openssl@1.1/cert.pem")
    database = client["ttds"]
    return database["invertedIndexFinal"],database["songMetaData"],database["lyricMetaData"]
end

function query(collection, term)
    doc = Mongoc.find_one(collection, Mongoc.BSON("""{ "_id" : "$term" }"""))
end

function main()
    batch_size = 50
    avgdl = 10

    terms = ["hello"]
    collection = establishConnection()
    index = Dict(term => Mongoc.as_dict(query(collection[1], term)) for term in terms)

    songMetaData = collection[2]
    lyricMetaData = collection[3]

    tracker = @time BM25(terms, "song",index,songMetaData,lyricMetaData)

    # print("Results:\n")
    # print(tracker)

    # song = true
    # terms = ["record", "breaker"]
    #
    # print("\n")
    #
    # tracker = @btime ps($terms, $index, $song)
    # print("\n")
    # print("Results:\n")
    # print(tracker)
    #
    # print("\n")
    #
    # proximity = 3
    # terms = ["on", "you"]
    # tracker = @btime prox($terms, $proximity, $index, $song)
    #
    # print("\n")
    # print("Results:\n")
    # print(tracker)
end
