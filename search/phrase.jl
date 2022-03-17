using PyCall

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
    matchingDocs = Set{Int}() # Set of all doc ids matching the query
    sequenceMap = Dict{Int, Dict{Int,Vector{Int}}}() # Dictionary mapping successive terms in the phrase to their view in the index

    if song
        # Song level phrase search
        for i in 1:length(phrase)
            posting = Dict{Int, Vector{Int}}(song_id => reduce(vcat,values(lines)) for (song_id, lines) in index[phrase[i]])
            sequenceMap[i] = i == 1 ? posting : Dict{Int,Vector{Int}}(song_id => listing for (song_id, listing) in posting if song_id ∈ keys(sequenceMap[i-1]))
        end
        matrixCount = Dict{Int,Int}()
        for song_id in keys(sequenceMap[length(phrase)])
            matching = false
            for i in 1:length(phrase)
                for position in sequenceMap[i][song_id]
                    updatedValue = get(matrixCount, position - i, 0) + 1
                    if updatedValue == length(phrase)
                        push!(matchingDocs, song_id)
                        matching = true
                        break
                    end
                    matrixCount[position - i] = updatedValue
                end
                matching && break
            end
        end
    else
        for i in 1:length(phrase)
            posting = Dict{Int, Vector{Int}}(line_id => positions for song in values(index[phrase[i]]) for (line_id, positions) in song)
            sequenceMap[i] = i == 1 ? posting : Dict{Int,Vector{Int}}(line_id => listing for (line_id, listing) in posting if line_id ∈ keys(sequenceMap[i-1]))
        end
        # matrixCount = Dict{Int,Int}()
        # for line_id in keys(sequenceMap[length(phrase)]) # Go through each line for which all terms appear
        #     matching = false
        #     for i in 1:length(phrase) # For every term in the phrase
        #         for position in sequenceMap[i][line_id]
        #             updatedValue = get(matrixCount, position - i, 0) + 1
        #             if updatedValue == length(phrase)
        #                 push!(matchingDocs, line_id)
        #                 matching = true
        #                 break
        #             end
        #             matrixCount[position - i] = updatedValue
        #         end
        #         matching && break
        #     end
        # end
    end
    matchingDocs
end

function main()
    index = load_pickle("search/Test_Lyrics_Eminem_index")
    index = convert(Dict{String, Dict{Int,Dict{Int,Vector{Int}}}}, index)
    @elapsed phraseSearch(["you"], index, true)
end
main()