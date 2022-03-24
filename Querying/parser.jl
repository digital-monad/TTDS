# using ParserCombinator
include("./search.jl")
include("./setOperations.jl")

# # the AST nodes we will construct, with evaluation via calc()

# # the AST nodes we will construct, with evaluation via calc()

# abstract type Node end
# Base.:(==)(n1::Node, n2::Node) = n1.val == n2.val
# # calc(n::String) = print(n)
# calc(n::SubString{String}) = print(n)

# struct NOT<:Node val end
# calc(n::NOT) = print(calc(n.val))

# struct AND<:Node val end
# calc(s::AND) = print(map(calc, s.val))

# struct OR<:Node val end
# calc(s::OR) = print(map(calc, s.val))



# # the grammar (the combinators!)

# term = Delayed()
# val = E"(" + term + E")" | p"\w+|\s+"

# neg = Delayed()       # allow multiple (or no) negations (eg ---3)
# neg.matcher = val | (E"~" + neg > NOT)

# andtax = E"&&" + neg
# and = neg + (andtax)[0:end] |> AND

# ortax = E"||" + neg
# term.matcher = neg + (ortax)[0:end] |> OR

# all = term + Eos()


# and test

# this prints 2.5


# and test

# this prints 2.5

##########
# I tried ;( -a
##########

pushfirst!(pyimport("sys")."path", "")

py"""
from Querying import QueryParser
x = QueryParser.QueryParser()
def query(query,isSong):
    return x.query(query,isSong)
"""

function query(query,isSong)
    parsed = py"query"(query,isSong)

    return resovleQuery(parsed)
end

function resovleQuery(clause)
    if clause[1] == "call_BM25"
        return call_BM25(clause[2],clause[3])
    end 
    if clause[1] == "call_prox"
        return call_prox(clause[2],clause[3],clause[4],clause[5])
    end 
    if clause[1] == "call_ps"
        return call_BM25(clause[2],clause[3])
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