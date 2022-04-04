using PyCall
using BenchmarkTools
using DataStructures
using Traceur
using Mongoc
using BSON
using DataFrames
using TimerOutputs
using Pickle
using CSV	
pushfirst!(pyimport("sys")."path", "")

@pyimport re

flag = true
songMetaData = Dict{String, Dict{Any, Any}}()
lyrics = DataFrame(CSV.File("out.csv"))
lyricMetaData= Dict{String, Dict{Any,Any}}()
current_line_id = 0

function preprocessSongLyricsMetadata(songLyrics)
    preprocessedLines = []

    pos = 0

    for line in split(songLyrics,"\n")

        stemmedLineTokens, pos = preprocessMetadata(line, pos)
        
        if length(stemmedLineTokens) > 0
            append!(preprocessedLines,stemmedLineTokens)
        end
    end

    return preprocessedLines
end

function preprocessMetadata(sentence, pos)
    regex = raw"\W+"
    tokens = re.sub(regex, " ",sentence)
    
    caseTokens = split(tokens,",")
    stemmedLineTokens = []

    for word in caseTokens
        word = string(word)
        append!(stemmedLineTokens, (word,pos))
        pos += 1
    end
    return stemmedLineTokens, pos
end

function processSong(song)
    global current_line_id
    global lyricMetaData
    lyrics = song[9]
    preprocessed_lyrics_metadata = preprocessSongLyricsMetadata(lyrics)
    song_id = string(song[1])
    for line in preprocessed_lyrics_metadata
        line_id = current_line_id
        line_id = string(line_id)
        tokens = [token for token in line]
        inner_dict = Dict{String, Any}()
        inner_dict["song_id"] = song_id
        inner_dict["length"] = length(line)
        inner_dict["text"] = join(tokens, " ")
        lyricMetaData[line_id] = inner_dict
        current_line_id += 1
    end
end


function indexFile()
    global lyrics
    #cols = [lyrics[i, :] for i in lyrics]
    songs = [row for row in eachrow(lyrics)]
    i = 0
    for song in songs
        print(i)
        print("\n")
        i += 1
        song = Tuple(song)
        processSong(song)
    end
end


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

"""
    phraseSearch(phrase::Vector{String}, index::Dict, song::Bool)
Compute n-term phrase search through index. `song` determines whether to perform
song level or line level search. Return set of document ids.

Compute n-term phrase search through index. `song` determines whether to perform
song level or line level search. Return set of document ids.

# Examples
````jldoctest
julia> phraseSearch(["Teenage", "wasteland"], index, false)
{24524,32889}
````
"""
function phraseSearch(phrase, index, song)
    results = Vector{Int}()
    common_songs = mapreduce(token -> keys(index[token]), ∩, phrase)
    irrelevant = Set{String}(["_id", "song_df", "tf", "line_df"])
    reduceSet = zeros(Int,5000)
    if song
        for song in common_songs
            song ∈ irrelevant && continue
            postings = (Base.Iterators.flatten(values(delete!(index[term][song], "tf"))) for term in phrase)
            term_no = 0
            for term_positions in postings
                for pos in term_positions
                    pos - term_no < 0 && continue
                    reduceSet[pos - term_no + 1] += 1
                    if reduceSet[pos - term_no + 1] == length(phrase)
                        push!(results, parse(Int,song))
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
                            push!(results, parse(Int,line))
                            break
                        end
                    end
                    term_no += 1
                end
                reduceSet .= zero(Int)
            end
        end
    end
    df = DataFrame(id=results, score=0)
    #print(df)

    df
end

function BM25(query,isSong, index, lyric_metadata)

    global songMetaData
    global lyricMetaData

    heap = MutableBinaryMinHeap{Float64}()
    tracker = Dict{Int64, String}()
    scores = Dict{String, Float64}()
    handles = Dict{String, Int64}()

    k1 = 1.5
    b = 0.75
    if isSong
        N = 1307152
        for term in query # SIMD vectorisation
            songs = collect(keys(index[term]))
            filter!(e->e∉["song_df","line_df","_id"],songs) # Lazy filter
	    metadatas = Dict(song => songMetaData[song] for song in songs)
            term_docs = length([i for i in keys(index[term])]) - 3 # Convert list
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
            if term in keys(index)
                i = 0
                for song in keys(index[term])
                    lyrics = index[term][song]
                    if i < 3
                        i += 1
                        continue
                    end
                    term_docs += (length(keys(index[term][song]))-1)
                    append!(docs, string.(collect(keys(lyrics))))
                end
            end
            if term_docs>0
                for song in keys(index[term])
                    filter!(e->e∉["tf"],docs)
                    metadatas = Dict(lyric => Mongoc.as_dict(querier(lyric_metadata, lyric)) for lyric in docs)
                    #metadatas = Dict(lyric => lyricMetaData[lyric] for lyric in docs)
                    for lyric in keys(index[term][song])
                        if lyric in keys(metadatas)
                            docs = collect(keys(index[term][song]))
                            term_freqs_in_doc = length(index[term][song][lyric])
                            dl = metadatas[lyric]["length"]
                            score_term = calc_BM25(N, term_docs, term_freqs_in_doc, k1, b, dl, 10)
                            add_score(lyric,score_term,heap,tracker,handles,scores)
                        end
                    end
                end
            end
        end
    end

    df = DataFrame(scores)

    colnames = names(df)

    dfl = stack(df, colnames)

    dfl = rename(dfl, :variable => :id, :value => :score)

    max = maximum(dfl[!,:score]) 

    if max == 0
        max = 1 
    end
    
    dfl.score = dfl.score / max
    
    dfl

end


function proximitySearch(term1, term2, proximity, index, song)
    irrelevant = Set{String}(["_id", "song_df", "tf", "line_df"])
    if length(keys(index[term1])) > length(keys(index[term2]))
        shorter = keys(index[term2])
        longer = keys(index[term1])
    else
        shorter = keys(index[term1])
        longer = keys(index[term2])
    end
    results = Vector{Int}()

    if song
        for song in shorter
            song ∈ irrelevant && continue
            if song ∈ longer
                orderedLines1 = sort!(OrderedDict(parse(Int, x) => y for (x,y) in delete!(index[term1][song], "tf")))
                orderedLines2 = sort!(OrderedDict(parse(Int, x) => y for (x,y) in delete!(index[term2][song], "tf")))
                posting1 = Base.Iterators.Stateful(Base.Iterators.flatten(values(orderedLines1))) # Positions of term 1 in song
                posting2 = Base.Iterators.Stateful(Base.Iterators.flatten(values(orderedLines2))) # Positions of term 2 in song

                matching = false
                ϑ = Base.Iterators.peek(posting2)
                for pos1 in posting1
                    # println("Position of thriller : $pos1")
                    # println("Position of fight : $ϑ")
                    matching = false
                    if abs(ϑ - pos1) <= proximity
                        push!(results, parse(Int,song))
                        break
                    end
                    if pos1 > ϑ
                        for pos2 in posting2
                            # println("Position of fight : $pos2")
                            if abs(pos2 - pos1) <= proximity
                                push!(results, parse(Int,song))
                                matching = true
                                break
                            end
                            ϑ = pos2
                            pos2 >= pos1 && break
                        end
                        matching && break
                    end
                end
            end
        end
    else
        for song in shorter
            song ∈ irrelevant && continue
            if song ∈ longer
                l1 = keys(index[term1][song])
                l2 = keys(index[term2][song])
                for line in l1
                    line == "tf" && continue
                    if line ∈ l2
                        # Perform linear merge over line positions
                        positions1 = index[term1][song][line]
                        positions2 = index[term2][song][line]
                        ptr1, ptr2 = (1,1)
                        while ptr1 <= length(positions1) && ptr2 <= length(positions2)
                            pos1 = positions1[ptr1]
                            pos2 = positions2[ptr2]
                            if abs(pos1 - pos2) <= proximity
                                push!(results, parse(Int,line))
                                break
                            end
                            if pos1 - pos2 > 0 # ptr1 is pointing at a larger position
                                ptr2 += 1
                            else
                                ptr1 += 1
                            end
                        end
                    end
                end
            end
        end
    end
    df = DataFrame(id=results, score=0)
end

function calc_BM25(N, term_docs, term_freq_in_doc, k1, b, dl, avgdl)
    third_term = k1 * ((1-b) + b * (float(dl)/float(avgdl)))
    idf_param = log( (N-term_docs+0.5) / (term_docs+0.5) ) # Wikipedia says + 1 before taking log
    next_param = ((k1 + 1) * term_freq_in_doc) / (third_term + term_freq_in_doc)
    return round((next_param * idf_param),digits=4)
end

function establishConnection()
    client = Mongoc.Client("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
    database = client["ttds"]
    return database["invertedIndexFinal"], database["lyricMetaData"]
end

function querier(collection, term)
    doc = Mongoc.find_one(collection, Mongoc.BSON("""{ "_id" : "$term" }"""))

    if doc == nothing
        return Mongoc.BSON("{}")
    end

    return doc
end

function call_BM25(terms, isSong)

    global flag
    global songMetaData
    global lyricMetaData

    if flag
        #lyricMetaData = Pickle.load(open("./line_metadata.pickle"))
        songMetaData = Pickle.load(open("./song_metadata.pickle"))
        flag = false
    end
    
    collection = establishConnection()
    lyric_metadata = collection[2]
    index = Dict(term => Mongoc.as_dict(querier(collection[1], term)) for term in terms)
    open("test.txt", "w") do f
        write(f, string(typeof(index)),string(typeof(terms)),string(isSong))
    end

    results = BM25(terms, isSong, index,lyric_metadata)

    results

end

function call_ps(terms, isSong)

    global flag
    global songMetaData
    global lyricMetaData

    if flag
        #lyricMetaData = Picle.load(open("../metadata/line_metadata.pickle"))
        songMetaData = Pickle.load(open("song_metadata.pickle"))
        flag = false
    end
    
    collection = establishConnection()
    index = Dict(term => Mongoc.as_dict(querier(collection[1], term)) for term in terms)

    results = phraseSearch(terms, index, isSong)

    results

end

function call_prox(term1, term2, proximity, isSong)

    global flag
    global songMetaData
    global lyricMetaData

    terms = [term1,term2]

    if flag
        #lyricMetaData = Pickle.load(open("../metadata/line_metadata.pickle"))
        songMetaData = Pickle.load(open("song_metadata.pickle"))
        flag = false
    end

    collection = establishConnection()
    index = Dict(term => Mongoc.as_dict(querier(collection[1], term)) for term in terms)
    
    results = proximitySearch(term1, term2, proximity, index, isSong)

    results
end
