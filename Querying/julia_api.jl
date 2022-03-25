

# using ParserCombinator
include("./search.jl")
include("./setOperations.jl")

function resovleQuery(clause)
    if clause[1] == "call_BM25"
        return call_BM25(clause[2],clause[3])
    end 
    if clause[1] == "call_prox"
        return call_prox(clause[2],clause[3],clause[4],clause[5])
    end 
    if clause[1] == "call_ps"
        return call_ps(clause[2],clause[3])
    end 
    if clause[1] == "and"
        return and(resovleQuery(clause[2]),resovleQuery(clause[3]))
    end 
    if clause[1] == "or"
        return or(resovleQuery(clause[2]),resovleQuery(clause[3]))
    end 
    if clause[1] == "not"
        return not(clause[2],resovleQuery(clause[3]))
    end 
    print("hmmm not cool")
end

function runThisQuery(passedQuery)

    # julia indexing from 1 is a ball ache
    parsed = buildQuery(passedQuery)

    results = resovleQuery(parsed)

    return results

end

function buildQuery(query) 

    clause = []

    
    index = 3

    # if query[index] == 'a'

    #     push!(clause, "and")

        

    # elseif query[index] == 'o'

    # elseif query[index] == 'n'

    if query[index] == 'x'
        println("prox")
        # prox 
        push!(clause, "call_prox")
        
        # skip the , and ' 
        index = index + 5

        term1 = ""

        while(query[index] != ''')
            if query[index] != ' '
                term1 = term1 * query[index]
            end
            index = index + 1
        end

        push!(clause, term1)

        # skip the , 
        index = index + 4

        term2 = ""

        while(query[index] != ''')
            if query[index] != ' '
                term2 = term2 * query[index]
            end
            index = index + 1
        end

        push!(clause, term2)

        # skip the , 
        index = index + 3

        distance = ""

        while(query[index] != ',')
            if query[index] != ' '
                distance = distance * query[index]
            end
            index = index + 1
        end

        push!(clause, parse(Int64, distance))

        index = index + 2


        isSong = ""

        while(query[index] != ']')
            if query[index] != ' '
                isSong = isSong * query[index]
            end
            index = index + 1
        end

        if isSong == "True"
            push!(clause, true)
        else
            push!(clause, false)
        end

        return clause

    elseif query[index] == 'p' || query[index] == 'b' 
        # bm25
        # phrase
        if query[index] == 'p' 
            push!(clause, "call_ps")
        else 
            push!(clause, "call_BM25")
        end
        index = index + 6

        terms = []
        
   

        while(index < 1000)
            term = ""

            while(query[index] != ''')
                if query[index] != ' '
                    term = term * query[index]
                end
                index = index + 1
            end

            push!(terms, term)

            index = index + 1

            
            if query[index] == ']'
                break
            end
            
            index = index + 3

        end 

        push!(clause, terms)

        
        index = index + 1

        isSong = ""

        while(query[index] != ']')
            if query[index] != ' '
                isSong = isSong * query[index]
            end
            index = index + 1
        end

        if isSong == "True"
            push!(clause, true)
        else
            push!(clause, false)
        end

    end

    # if c == '['
    #     newclause, index = buildQuery(query[index:end], index)
    #     append!(clause, newclause)
    # elseif c == ']'
    #     break;
    # else 
    #     print("wrong")
    # end

    

    return clause
end

using Genie, Genie.Router

using Genie.Requests

route("/query") do
    return sort_scores(runThisQuery("$(getpayload(:query, "querrrryy"))"))
end

up()

