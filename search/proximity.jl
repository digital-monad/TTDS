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

function prox(terms, proximity, index, song)

    if length(keys(index[terms[1]])) > length(keys(index[terms[2]]))
        shorter = keys(index[terms[2]])
        longer = keys(index[terms[1]])
    else
        shorter = keys(index[terms[1]])
        longer = keys(index[terms[2]])
    end
    results = Vector{Int}()

    if song
        for song in shorter
            if song ∈ longer
                posting1 = Base.Iterators.flatten(values(index[terms[1]][song])) # Positions of term 1 in song
                posting2 = Base.Iterators.flatten(values(index[terms[2]][song])) # Positions of term 2 in song
                # λ1 = iterate(posting1)
                # Linear merge postings
                # while λ1 !== nothing && λ2 !== nothing
                #     pos1, state1 = λ1
                #     pos2, state2 = λ2
                #     if abs(pos1 - pos2) <= proximity
                #         push!(results, song)
                #         break
                #     end
                #     if pos1 - pos2 > 0 # ptr1 is pointing at a larger position
                #         λ2 = iterate(posting2, state2)
                #     else
                #         λ1 = iterate(posting1, state1)
                #     end
                # end
                finished = false
                ℵ = Base.Iterators.peel(posting2)
                pos2, posting2 = ℵ
                for pos1 in posting1
                    if abs(pos1 - pos2) <= proximity
                        push!(results, song)
                        finished = true
                        break
                    end
                    while pos2 < pos1
                        if ℵ === nothing
                            finished = true
                            break
                        end
                        pos2, posting2 = ℵ
                        if abs(pos1 - pos2) <= proximity
                            push!(results, song)
                            finished = true
                            break
                        end
                        ℵ = Base.Iterators.peel(posting2)
                    end
                    finished && break
                end
            end
        end
    else
        for song in shorter
            if song ∈ longer
                l1 = keys(index[terms[1]][song])
                l2 = keys(index[terms[2]][song])
                for line in l1
                    if line ∈ l2
                        # Perform linear merge over line positions
                        positions1 = index[terms[1]][song][line]
                        positions2 = index[terms[2]][song][line]
                        ptr1, ptr2 = (1,1)
                        while ptr1 <= length(positions1) && ptr2 <= length(positions2)
                            pos1 = positions1[ptr1]
                            pos2 = positions2[ptr2]
                            if abs(pos1 - pos2) <= proximity
                                push!(results, line)
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
    # @code_warntype prox(["on", "you"], 3, index, false)
    @benchmark prox($terms, $proximity, $index, $song)
    # @trace(prox(terms, proximity, index, song), modules=[Main])
end
main()