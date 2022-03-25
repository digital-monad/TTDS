

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

    return results

end

function buildQuery(query) 

    clause = []

    println("--Query--")
    println(query)
    println("---")

    # Skip to the identifying character 
    index = 3

    if query[index] == 'a' || query[index] == 'o'

        if query[index] == 'a'
            push!(clause, "and")
        else 
            push!(clause, "or")
        end

        # Skip to the first open bracket
        index = index + 4
        
        if query[index] == '['
        
            indexstart = index
            
            index = index + 1

            bracketcount = 1

            while(bracketcount != 0 && index < 1000)
                
                if query[index] == '['
                    bracketcount = bracketcount + 1     
                elseif query[index] == ']'
                    bracketcount = bracketcount - 1
                end

                index = index + 1
            end

            clause1 = buildQuery(query[indexstart:index-1])

            if query[index] != ','
                print("HMMMM")
            end

            index = index + 2

            if query[index] != '['
                print("HMMMM2")
            end
            
            indexstart = index

            index = index + 1

            bracketcount = 1

            while(bracketcount != 0 && index < 1000)
                
                if query[index] == '['
                    bracketcount = bracketcount + 1     
                elseif query[index] == ']'
                    bracketcount = bracketcount - 1
                end

                index = index + 1
            end

            clause2 = buildQuery(query[indexstart:index-1])
            
            push!(clause, clause1)
            
            push!(clause, clause2)

        else 
            print("Hmmmmm")
        end

    elseif query[index] == 'n'
        
        push!(clause, "not")

        index = index + 3

        idcount = ""

        while(query[index] != ',')
            if query[index] != ' '
                idcount = idcount * query[index]
            end
            index = index + 1
        end

        push!(clause, parse(Int64, idcount))

        index = index + 2

        if query[index] != '['
            print("hmmm not cool")
        end

        indexstart = index
            
        index = index + 1

        bracketcount = 1

        while(bracketcount != 0 && index < 1000)
            
            if query[index] == '['
                bracketcount = bracketcount + 1     
            elseif query[index] == ']'
                bracketcount = bracketcount - 1
            end

            index = index + 1
        end

        clause1 = buildQuery(query[indexstart:index-1])

        push!(clause, clause1)

    elseif query[index] == 'x'
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

    return clause
end

using Genie, Genie.Router

using Genie.Requests

route("/query") do
    return sort_scores(runThisQuery("$(getpayload(:query, "querrrryy"))"))
end

up()

