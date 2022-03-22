import pymongo

client = pymongo.MongoClient("mongodb+srv://group37:VP7SbToaxRFcmUbd@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority")

inverted_index_collection = client.ttds.invertedIndex

print(inverted_index_collection.count_documents({}))