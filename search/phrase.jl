using PyCall
using BenchmarkTools
using SparseArrays
using DataStructures
using Mongoc

py"""
import pickle
def load_pickle(file_name):
    with open(file_name + '.pickle', 'rb') as f:
        return pickle.load(f)
"""

load_pickle = py"load_pickle"


"""
    phraseSearch(phrase::Vector{String}, index::Dict, song::Bool)

Compute n-term phrase search through index. `song` determines whether to perform
song level or line level search. Return set of document ids.

# Examples
````jldoctest
julia> phraseSearch(["Teenage", "wasteland"], index, false)
{24524,32889}
````
"""
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
    matchingDocs
end

function ps(phrase, index, song)
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
    results
end

# length(phrase) ∈ sum([sparsevec(pos, ones(Int, length(pos))) for pos in Base.Iterators.map(i -> index[phrase[i]][song][line] .- (i-1),1:length(phrase))]) && (push!(results, line))

function establishConnection()
    client = Mongoc.Client("mongodb+srv://group37:VP7SbToaxRFcmUbd@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority&tlsCAFile=/usr/local/etc/openssl@1.1/cert.pem")
    database = client["ttds"]
    database["invertedIndexFinal"]
end


function query(collection, term)
    doc = Mongoc.find_one(collection, Mongoc.BSON("""{ "_id" : "$term" }"""))
end


function main()
    # index = load_pickle("search/Test_Lyrics_Eminem_index")
    # index = convert(Dict{String, Dict{Int,Dict{Int,Vector{Int}}}}, index)
    song = true
    terms = ["billi", "jean", "is", "not", "my", "lover", "she", "s", "just", "a", "girl"]
    # @benchmark phraseSearch($terms, $index, $song)

    collection = establishConnection()
    index = Dict(term => Mongoc.as_dict(query(collection, term)) for term in terms)
    # index = convert(Dict{String, Dict{String, Dict{String,Vector{Int}}}}, index)
    # @benchmark ps($terms, $index, $song)
    ps(terms, index, song)
    # keys(Mongoc.as_dict(query(collection, "rain")))
end
main()