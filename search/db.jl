import Mongoc



function establishConnection()
    client = Mongoc.Client("mongodb+srv://group37:VP7SbToaxRFcmUbd@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority&tlsCAFile=/usr/local/etc/openssl@1.1/cert.pem")
    database = client["ttds"]
    database["songMetaData"]
end


function query(collection)
    collect(collection)
end


function main()
    collection = establishConnection()
    query(collection)
end

main()