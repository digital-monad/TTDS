include("./search.jl")
include("./setOperations.jl")
pushfirst!(pyimport("sys")."path", "")
py"""
import OldParser as QueryParser
x = QueryParser.QueryParser()
def query(query,isSong):
    return x.query(query,isSong)
"""
function query(query,isSong)
    parsed = py"query"(query,isSong)

    return resovleQuery(parsed)
    return sort_scores(resovleQuery(parsed))
end

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
