import Mongoc



function establishConnection()
    client = Mongoc.Client("mongodb+srv://group37:VP7SbToaxRFcmUbd@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority")
    database = client["ttds"]
    collection = database["invertedIndex"]
end

establishConnection()