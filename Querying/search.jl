using PyCall
using BenchmarkTools
using DataStructures
using Traceur
using Mongoc
using BSON
using DataFrames
using TimerOutputs

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

function add_score(id,score,heap,tracker,handles,scores)
    max_size = 100000

    if id in keys(handles)
        score += scores[id]
    end

    scores[id] = score

    if length(heap) >= max_size 
        # discarded attempt
        if score <= first(heap)
            return
        end
        # Then we remove the smallest thing in heap
        ~, i = top_with_handle(heap)
        delete!(heap,i)
        delete!(tracker, handles[id])
        delete!(handles, id)

    end

    if id in keys(handles)
        update!(heap, handles[id], score)

    else 
        handles[id] = push!(heap, score)
        tracker[handles[id]] = id
    end

end

# function __remove_entry_if_exists(heap,tracker, handles, id)
#     if id in keys(tracker)
#         delete!(heap, tracker[id][0])
#         delete!(handles, tracker[id][0])
#         delete!(tracker, id)
#     end
# end

# function __cleanup(heap,tracker,handles)
#     max_size = 100000
#     while true
#         if length(heap) == 0
#             break
#         end
#         if length(heap) > max_size  # here we know that id is not removed, but we have exceeded the size limit
#             ~, i = top_with_handle(heap)
#             delete!(heap,i)
#             delete!(tracker, handles[i])
#             delete!(handles, i)
#             continue
#         end
#         break  # nothing was removed, so the cleanup has finished. Exit the loop
#     end
# end


function phraseSearch(phrase::Vector{String},index, song::Bool)
    matchingDocs = Vector{Int}() # Set of all doc ids matching the query
    if song
        common_songs = mapreduce(token -> keys(index[token]), ∩, phrase)
        irrelevant = Set{String}(["_id", "song_df", "tf"])
        reduceSet = zeros(Int,5000)
        for song in common_songs
            song ∈ irrelevant && continue
            postings = (Base.Iterators.flatten(values(index[term][song])) for term in phrase)
            term_no = 0
            for term_positions in postings
                for pos in term_positions
                    pos - term_no < 0 && continue
                    reduceSet[pos - term_no + 1] += 1
                    if reduceSet[pos - term_no + 1] == length(phrase)
                        push!(matchingDocs, parse(Int,song))
                        break
                    end
                end
                term_no += 1
            end
            reduceSet .= zero(Int)
        end
    else
        sequenceMap = Dict{Int, Dict{Int,Vector{Int}}}() # Dictionary mapping successive terms in the phrase to their view in the index
        for i in 1:length(phrase)
            posting = Dict{Int, Vector{Int}}(line_id => positions for song in values(index[phrase[i]]) for (line_id, positions) in song)
            sequenceMap[i] = i == 1 ? posting : Dict{Int,Vector{Int}}(line_id => listing for (line_id, listing) in posting if line_id ∈ keys(sequenceMap[i-1]))
        end
        matrixCount = Dict{Int,Int}()
        for line_id in keys(sequenceMap[length(phrase)]) # Go through each line for which all terms appear
            matching = false
            for i in 1:length(phrase) # For every term in the phrase
                for position in sequenceMap[i][line_id]
                    updatedValue = get(matrixCount, position - i, 0) + 1
                    if updatedValue == length(phrase)
                        push!(matchingDocs, parse(Int,line_id))
                        matching = true
                        break
                    end
                    matrixCount[position - i] = updatedValue
                end
                matching && break
            end
        end
    end
    df = DataFrame(id=matchingDocs, score=0)
    print(df)

    df

end

function ps(phrase, index, song)
    heap = MutableBinaryMinHeap{String}()
    tracker = Dict{String, Float64}()
    common_songs = mapreduce(token -> keys(index[token]), ∩, phrase)
    irrelevant = Set{String}(["_id", "song_df", "tf"])
    reduceSet = zeros(Int,5000)
    if song
        for song in common_songs
            song ∈ irrelevant && continue
            postings = (Base.Iterators.flatten(values(index[term][song])) for term in phrase)
            term_no = 0
            for term_positions in postings
                for pos in term_positions
                    pos - term_no < 0 && continue
                    reduceSet[pos - term_no + 1] += 1
                    if reduceSet[pos - term_no + 1] == length(phrase)
                        add_score(song,0,heap,tracker)
                        break
                    end
                end
                term_no += 1
            end
            reduceSet .= zero(Int)
        end
    else
        for song in common_songs
            song ∈ irrelevant && continue
            # Go through the lines that are common within each song
            common_lines = mapreduce(token -> keys(index[token][song]), ∩, phrase)
            for line in common_lines
                line == "tf" && continue
                postings = (index[token][song][line] for token in phrase)
                term_no = 0
                for token in postings
                    for pos in token
                        pos - term_no < 0 && continue
                        reduceSet[pos - term_no + 1] += 1
                        if reduceSet[pos - term_no + 1] == length(phrase)
                            add_score(line,0,heap,tracker)
                            break
                        end
                    end
                    term_no += 1
                end
                reduceSet .= zero(Int)
            end
        end
    end
    DataFrame(tracker)
end

function BM25(query,isSong,index,song_metadata,lyric_metadata)
    
    heap = MutableBinaryMinHeap{Float64}()
    tracker = Dict{Int64, String}()
    scores = Dict{String, Float64}()
    handles = Dict{String, Int64}()

    k1 = 1.5
    b = 0.75
    if isSong
        N = 1307152
        for term in query
            print(term)
            songs = collect(keys(index[term]))
            filter!(e->e∉["song_df","line_df","_id"],songs) # Lazy filter
            @time metadatas = Dict(song => Mongoc.as_dict(querier(song_metadata, song)) for song in songs)
            term_docs = length([i for i in keys(index[term])]) - 3
            if term_docs>0
                for song in songs
                    term_freq_in_doc = index[term][song]["tf"]
                    dl = metadatas[song]["length"]
                    score = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, 1000)
                    add_score(song,score,heap,tracker,handles,scores)
                end
            end
        end
    else
        N = 60000000
        for term in query
            term_docs = 0
            docs = Vector{String}()
            metadatas = Dict{Any,Any}()
            if term in keys(index)
                for song in keys(index[term])
                    term_docs += length(keys(index[term][song]))
                    vcat(docs, collect(keys(index[term][song])))
                end
            end
            if term_docs>0
                for song in keys(index[term])
                    filter!(e->e∉["tf"],docs)
                    @timeit "1" metadatas = Dict(lyric => Mongoc.as_dict(querier(lyric_metadata, lyric)) for lyric in docs)
                    for lyric in keys(index[term][song])
                        docs = collect(keys(index[term][song]))
                        term_freqs_in_doc = length(index[term][song][lyric])
                        dl = metadatas[lyric]["length"]
                        score_term = calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, 10)
                        add_score(lyric,score_term,heap,tracker,handles,scores)
                    end
                end
            end
        end
    end
    
    print_timer()

    df = DataFrame(scores)

    colnames = names(df)

    dfl = stack(df, colnames)

    colnames = ["id","score"]

    names!(dfl, Symbol.(colnames))

    # sort!(dfl, rev=true, :value)

    print(dfl)

    dfl

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

function querier(collection, term)
    doc = Mongoc.find_one(collection, Mongoc.BSON("""{ "_id" : "$term" }"""))

    if doc == nothing
        return Mongoc.BSON("{}")
    end

    return doc
end

function call_BM25(terms, isSong)
    
    collection = establishConnection()
    index = Dict(term => Mongoc.as_dict(querier(collection[1], term)) for term in terms)

    songMetaData = collection[2]
    lyricMetaData = collection[3]

    results = @time BM25(terms, true, index, songMetaData, lyricMetaData)

    results

end

function call_ps(terms, isSong)

    collection = establishConnection()
    index = Dict(term => Mongoc.as_dict(querier(collection[1], term)) for term in terms)

    songMetaData = collection[2]
    lyricMetaData = collection[3]

    results = @time phraseSearch(terms, index, isSong)


    results
    
end

