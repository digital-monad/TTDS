using PyCall
using BenchmarkTools
using SparseArrays
using DataStructures

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
function phraseSearch(phrase::Vector{String}, index::Dict, song::Bool)
    matchingDocs = Vector{Int}() # Set of all doc ids matching the query

    if song
        # Song level phrase search
        common_songs = mapreduce(token -> keys(index[token]), ∩, phrase)
        reduceSet = zeros(Int,5000)
        for song in common_songs
            postings = (Base.Iterators.flatten(values(index[term][song])) for term in phrase)
            term_no = 0
            for term_positions in postings
                for pos in term_positions
                    pos - term_no < 0 && continue
                    reduceSet[pos - term_no + 1] += 1
                    if reduceSet[pos - term_no + 1] == length(phrase)
                        push!(matchingDocs, song)
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
                        push!(matchingDocs, line_id)
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
    if song
        reduceSet = zeros(Int,5000)
        for song in common_songs
            postings = (Base.Iterators.flatten(values(index[term][song])) for term in phrase)
            term_no = 0
            for term_positions in postings
                for pos in term_positions
                    pos - term_no < 0 && continue
                    reduceSet[pos - term_no + 1] += 1
                    if reduceSet[pos - term_no + 1] == length(phrase)
                        push!(results, song)
                        break
                    end
                end
                term_no += 1
            end
            reduceSet .= zero(Int)
        end
    else
        for song in common_songs
        end
    end
    results
end

# length(phrase) ∈ sum([sparsevec(pos, ones(Int, length(pos))) for pos in Base.Iterators.map(i -> index[phrase[i]][song][line] .- (i-1),1:length(phrase))]) && (push!(results, line))


function main()
    index = load_pickle("search/Test_Lyrics_Eminem_index")
    index = convert(Dict{String, Dict{Int,Dict{Int,Vector{Int}}}}, index)
    song = false
    terms = ["song", "and", "danc"]
    # @benchmark phraseSearch($terms, $index, $song)
    phraseSearch(terms, index, song)
end
main()