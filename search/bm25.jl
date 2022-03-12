using PyCall

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
    if length(heap) >= max_size && score <= tracker[heap[0]]
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
        delete!(tracker[id])
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
            delete!(tracker[id])
            continue
        end
        break  # nothing was removed, so the cleanup has finished. Exit the loop
    end
end






function BM25(query, avgdl, search_type,index,song_metadata,lyric_metadata) # Assuming query is preprocesses into tokens
    # batch_size = 50
    heap = MutableBinaryMinHeap{Int}()
    tracker = Dict{Int, Float64}()
    k1 = 1.5 # Constants
    b = 0.75 # Constants
    if search_type == "song"
        N = length(song_metadata)
        for term in query # Iterates each term in query
            term_docs = length(keys(index[term])) # Number of songs term appears in
            if term_docs>0
                for song in keys(index[term]) # Iterates each song for this given term
                    term_freq_in_doc = 0
                    for line in keys(index[term][song])
                        term_freq_in_doc += length(index[term][song][line]) # Number of instances of term in given song
                    end
                    dl = song_metadata[song]["length"]
                    # We are now calculating BM25 for a given term in query for a given song
                    score_term = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                    # We now add this to 'results_dict'
                    results_dict[song] += score_term
                    add_score(song,score_term,heap,tracker)
                end
            end
        end
    elseif search_type == "lyric"
        N = length(lyric_metadata)
        for term in query  # Iterates each term in query
            term_docs = 0
            if term in keys(index)
                for song in keys(index[term]) # Iterates each song for this given term
                    term_docs += length(keys(index[term][song])) # Number of lyrics term appears ins
                end
                for song in keys(index[term])
                    for lyric in keys(index[term][song])
                        term_freq_in_doc = length(index[term][song][lyric])
                        dl = lyric_metadata[lyric]["length"]
                        # We are now calculating BM25 for a given term in query for a given song
                        score_term = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
                        # We now add this to 'results_dict', which will already contain somevalue if previous term apeared in given song
                        add_score(lyric,score_term,heap,tracker)
                    end
                end
            end
        end
    end
    return heap
end

function calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
    third_term = K(k1, b, dl, avgdl)
    idf_param = log( (N-term_docs+0.5) / (term_docs+0.5) ) # Wikipedia says + 1 before taking log
    next_param = ((k1 + 1) * term_freq_in_doc) / (third_term + term_freq_in_doc)
    return round((next_param * idf_param),digits=4)
end

function K( k1, b, d, avgdl)
    return k1 * ((1-b) + b * (float(d)/float(avgdl)) )
end

function ranked_retrieval(query, search_type, show_results,index,song_metadata,lyric_metadata)
    avgdl = 10
    results = BM25(query, avgdl, search_type,index,song_metadata,lyric_metadata)
    # result_ids = [item[0] for item in results.getTopN(show_results)]
    # return result_ids
    return results
end

function main()
    batch_size = 50
    # comment this out if youve got pickle files
    index = load_pickle("/Users/joshmillar/ttds/ttds_group/TTDS/search/Test_Lyrics_Eminem_index.pickle")
    song_metadata = load_pickle("/Users/joshmillar/ttds/ttds_group/TTDS/search/Test_Lyrics_Eminem_song_metadata.pickle")
    lyric_metadata = load_pickle("/Users/joshmillar/ttds/ttds_group/TTDS/search/Test_Lyrics_Eminem_line_metadata.pickle")
    index = convert(Dict{String, Dict{Int, Dict{Int, Vector{Int}}}}, index)
    song_metadata = convert(Dict{Int, Dict{String, Any}}, song_metadata)
    lyric_metadata = convert(Dict{Int, Dict{String, Any}}, lyric_metadata)

    # uncomment this if you havent got pickle files
    # index = {"hi": {'song1': {0: [1,2,3], 13: [1,2,3]}, 'song2':{1:[1]}}, "good": {'song1': {1: [2,3], 11: [1,2,3]}, 'song2':{2: [1,2,3], 14: [1,2,4,6,7,8]}}}
    # song_metadata = {"song1":{"genre": "pop", "artist": "adele", "len": 13,}, "song2":{"genre": "pop","artist": "adele", "len": 19,}}
    # lyric_metadata = {0:{"song": "song1", "len": 8,}, 1:{"song": "song1", "len": 8,}, 11:{"song": "song1", "len": 8,}, 13:{"song": "song1", "len": 8,}, 2:{"song": "song2", "len": 8,}, 3:{"song": "song2", "len": 8,}, 14:{"song": "song2", "len": 8,}, 17:{"song": "song2", "len": 8,} }

    # tracker = ranked_retrieval(["chorus","hurt","pain"], "song", batch_size,index,song_metadata,lyric_metadata)
    tracker = @time ranked_retrieval(["hurt"], "lyric", batch_size,index,song_metadata,lyric_metadata)

    print("Results:\n")
    print(tracker)
end
