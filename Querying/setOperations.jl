# using Pkg
# pkg"add DataFrames"

using DataFrames

function and(df1, df2)

    fullDf = innerjoin(rename(df1, :score => :z1), rename(df2, :score => :z2); on= :id) 

    if isempty(fullDf)
        return DataFrame(id=[],score=[])
    end

    fullDf.score = sum(eachcol(fullDf[!, r"z"]))
    
    max = maximum(fullDf[!,:score]) 

    if max == 0
        max = 1 
    end
    
    fullDf.score = fullDf.score / max
    
    return hcat(fullDf[!, :id],fullDf[!, :score])

end

function or(df1, df2)
    
    fullDf = coalesce.(outerjoin(rename(df1, :score => :z1), rename(df2, :score => :z2); on= :id),0)
        
    fullDf = transform(fullDf, [:z1, :z2] => ByRow((z1_elm,z2_elm) -> max(z1_elm,z2_elm)) => :score)
        
    return hcat(fullDf[!, :id],fullDf[!, :score])

end


function not(size, df)
    new_df = DataFrame(id=0:size, score=0)
    return antijoin(new_df, df; on= :id)
end 

function sort_and_convert(unsorted_query_results)
    
    sort!(unsorted_query_results, rev=true, :score)
    
    print(unsorted_query_results)

    return PyObject(unsorted_query_results[!,:id])
end 
