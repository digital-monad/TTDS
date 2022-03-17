using PyCall
using BenchmarkTools
using Traceur

py"""
import pickle
def load_pickle(file_name):
    with open(file_name + '.pickle', 'rb') as f:
        return pickle.load(f)
"""

load_pickle = py"load_pickle"


function proximity(terms, proximity, index, song)
    common_songs = keys(index[terms[1]]) ∩ keys(index[terms[2]])
    results = Set{Int}()

    if song
        for song ∈ common_songs
            ohyeah = true
            while ohyeah
                for line1 ∈ keys(index[terms[1]][song])
                    for line2 ∈ keys(index[terms[2]][song])
                        what = [abs(x-y) for x ∈ index[terms[1]][song][line1] for y ∈ index[terms[2]][song][line1]]
                        if length(filter(x -> x <= proximity, what)) > 0
                            push!(results, song)
                            ohyeah = false
                        end
                    end
                end
                ohyeah = false
            end
        end
        return results
    end
end


function prox(terms, proximity, index, song)

    if length(keys(index[terms[1]])) > length(keys(index[terms[2]]))
        shorter = keys(index[terms[2]])
        longer = keys(index[terms[1]])
    else
        shorter = keys(index[terms[1]])
        longer = keys(index[terms[2]])
    end
    results = Set{Int}()

    if song
        for song in shorter
            if song ∈ longer
                posting1 = Base.Iterators.flatten(values(index[terms[1]][song])) # Positions of term 1 in song
                posting2 = Base.Iterators.flatten(values(index[terms[2]][song])) # Positions of term 2 in song
                λ1 = iterate(posting1)
                λ2 = iterate(posting2)
                # Linear merge postings
                while λ1 !== nothing && λ2 !== nothing
                    pos1, state1 = λ1
                    pos2, state2 = λ2
                    if abs(pos1 - pos2) <= proximity
                        push!(results, song)
                        break
                    end
                    if pos1 - pos2 > 0 # ptr1 is pointing at a larger position
                        λ2 = iterate(posting2, state2)
                    else
                        λ1 = iterate(posting1, state1)
                    end
                end
            end
        end
    else
        for song in shorter
            if song ∈ longer
                for line in keys(index[terms[1]][song])
                    if line ∈ keys(index[terms[2]][song])
                        # Perform linear merge over line positions
                        positions1 = index[terms[1]][song][line]
                        positions2 = index[terms[2]][song][line]
                        ptr1, ptr2 = (1,1)
                        while ptr1 <= length(positions1) && ptr2 <= length(positions2)
                            pos1 = positions1[ptr1]
                            pos2 = positions2[ptr2]
                            if abs(pos1 - pos2) <= proximity
                                push!(results, song)
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
    results
end


function main()
    index = load_pickle("search/Test_Lyrics_Eminem_index")
    index = convert(Dict{String, Dict{Int,Dict{Int,Vector{Int}}}}, index)
    proximity = 3
    song = true
    terms = ["on", "you"]
    # @time prox(["on", "you"], 3, index, true)
    # @benchmark prox($terms, $proximity, $index, $song)
    @trace(prox(terms, proximity, index, song), modules=[Main])
end
main()