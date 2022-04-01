
# Setup Flask and MongoDB - integration for backend and database
from flask import Flask, jsonify, render_template, request
import configparser, pymongo, os, requests
import Querying.QueryParser as qp
import requests
import query_complete as qc

app = Flask(__name__)

queryParser = qp.QueryParser()

config = configparser.ConfigParser()
config.read('settings.ini')

# NOTE: Make sure you have a local MongoDB db instance for lyricMetaData, songMetaData
uri = 'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false'

client = pymongo.MongoClient(uri)

@app.route("/", methods=['GET','POST'])
def show_main_page():
    return render_template('index.html')

# Integrates Python query_complete file
# Cannot return a list from Flask View - must return Jsonify instead
@app.route("/autocomplete", methods=['GET'])
def autocomplete():
    query_str = 'Ligma' # Default query - shouldn't affect autocomplete
    if request.args.get('q'):
        query_str = request.args.get('q')

    outcomes_list = query_completion.query(query_str)

    filtered_dict = [k for k in outcomes_list if query_str in k]

    return jsonify(matching_results=filtered_dict)


# Obtain list of relevant songs
def get_songs(advanced_filters, page_size, page_num):

    print('Obtain songs by song search')

    # Obtain query from front-end
    song_name = 'Some Song' # Song cannot be empty
    isSong = True
    if request.args.get('q'):
        song_name = request.args.get('q')

    # NOTE: How does QueryParser determine which query algo to use??
    #parsed = str(queryParser.parseQuery('#(10,proximity,search)', True))
    parsed = str(queryParser.parseQuery(song_name, True)) # This is just default
    #parsed = queryParser.parseQuery('"test" && spiderman')
    
    #TODO: This list of lyrics line_ids is fixed - make sure they are dynamic from Julia side
    song_ids = ["1158679", "1158653", "1158688", "1158655", "1158651", "1158652", "1158664", "1158673"] 

    try:
        res = requests.get('http://127.0.0.1:8000/search?q='+str(parsed))
        # NOTE: Current response is 'call_BM25Any[query]false'
        # Successful response should be something a string of list of lyrics ids
        print(res.text)

        # `song_ids` attribute should be updated...
        # song_ids = res.text
    except:
        print("Request Exception")
        print("Ensure Genie server is running?")
        raise BaseException("Some Exception")

    and_query = list()
    and_query.append({"_id": { "$in": song_ids }})
    
    # Integrate proper advanced search support
    if len(advanced_filters) > 0:
        if advanced_filters[0].get('artist'):
            and_query.append({"artist": advanced_filters[0].get('artist')})
        if advanced_filters[0].get('album'):
            and_query.append({"album": advanced_filters[0].get('album')})
        if advanced_filters[0].get('year'):
            and_query.append({"year": advanced_filters[0].get('year')})

    songs_list = list(client.ttds.songMetaData
        .find(
                {"$and": and_query}
            )
        .limit(50)
    )
    
    sorted_song_dict = {d['_id']: d for d in songs_list}  # sentence_id -> sentence_dict
    
    # Obtain new list of ORDERED ids - allow advanced search
    new_ids = []
    for id in song_ids:
        if id in sorted_song_dict:
            new_ids.append(id)

    sorted_song_list = [sorted_song_dict[i] for i in new_ids]
    
    new_sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return new_sorted_song_list

# Obtain list of relevant songs based on lyrics
def get_songs_based_on_lyrics(advanced_filters, page_size, page_num):

    print('Obtain songs based on lyrics search')

    # Obtain query input from front-end
    lyrics_expr = 'dobra' # Default query input from song_id 728119
    isSong = False
    if request.args.get('q'):
        lyrics_expr = request.args.get('q')

    # NOTE: How does QueryParser determine which query algo to use??
    #parsed = str(queryParser.parseQuery('#(10,proximity,search)', True))
    parsed = str(queryParser.parseQuery(lyrics_expr, isSong)) # This is just default
    #parsed = queryParser.parseQuery('"test" && spiderman')

    #TODO: This list of lyrics line_ids is fixed - make sure they are dynamic from Julia side
    lyrics_ids = ["54160733", "54161020", "2", "3", "54160897", "54161020", "1", "69", "6969"] # Currently no constraints

    try:
        res = requests.get('http://127.0.0.1:8000/search?q='+str(parsed))
        # NOTE: Current response is 'call_BM25Any[query]false'
        # Successful response should be something a string of list of lyrics ids
        print(res.text)

        # lyrics_ids = res.text
    except:
        print("Request Exception")
        print("Ensure Genie server is running?")
        raise BaseException("Some Exception")


    # TODO: Aggregate lyricMetaData for songMetaData
    # Determine final limit for querying results back to front-end
    lyrics = client.ttds.lyricMetaData.aggregate([
        { "$match": {"_id": {"$in": lyrics_ids }} },
        {
            "$lookup": {
                "from" : "songMetaData",
                "localField" : "song_id", 
                "foreignField" : "_id",
                "as" : "song_details"
            }
        },
        {
            "$limit": 50
        },
    ])
    lyrics_list = list(lyrics)
    lyrics_list_filtered = list()

    # Use advanced search to remove songs in lyrics_ids list to filter
    for lyrics_object in lyrics_list:
        artist = lyrics_object['song_details'][0].get('artist')
        album = lyrics_object['song_details'][0].get('album')
        year = int(lyrics_object['song_details'][0].get('year'))

        if len(advanced_filters) > 0:
            if artist == advanced_filters[0].get('artist', artist) and album == advanced_filters[0].get('album', album) and year == advanced_filters[0].get('year', year):
                lyrics_list_filtered.append(lyrics_object)
        else:
            lyrics_list_filtered = lyrics_list
        

    # Ensure ordered documents are conducted
    sorted_lyrics_dict = {d['_id']: d for d in lyrics_list_filtered}  # sentence_id -> sentence_dict
    
    # Obtain new list of ORDERED ids - allow advanced search
    new_ids = []
    for id in lyrics_ids:
        if id in sorted_lyrics_dict:
            new_ids.append(id)

    sorted_song_list = [sorted_lyrics_dict[i] for i in new_ids]
    
    new_sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return new_sorted_song_list


ROWS_PER_PAGE = 6 # TODO: SHOULD BE CHANGED

# Unnecessary?
@app.route('/search', methods=['GET', 'POST'])
def display_search_first_results():
    advanced_filters = []
    relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, 1)
    return render_template('search.html', data = relevant_docs)
# Unnecessary?

@app.route('/search/page=<int:page>', methods=['GET', 'POST'])
def display_search_results(page):

    advanced_filters = []
    artist_str = ''
    album_str = ''
    year_str = ''

    if request.args.get('artist', False):
        artist_str = request.args.get('artist')
        advanced_filters.append({'artist': request.args.get('artist')})
    if request.args.get('album', False):
        album_str = request.args.get('album')
        advanced_filters.append({'album': request.args.get('album')})
    if request.args.get('year', False):
        year_str = request.args.get('year')
        year_int = int(request.args.get('year'))
        advanced_filters.append({'year': year_int})

    # TODO: Modify try/exception blocks to handle misfailures
    # Checks if script should conduct song search or lyrics search
    search_by_songs_toggle = request.args.get('sbs', False)
    print(search_by_songs_toggle)
    if search_by_songs_toggle == 'on':
        relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, page)
        return render_template('search.html', data = relevant_docs, sbs = 'on', artist = artist_str, album = album_str, year = year_str, page = page)

    # SEARCH BY SONG LYRICS
    else:
        relevant_docs = get_songs_based_on_lyrics(advanced_filters, ROWS_PER_PAGE, page)
        return render_template('searchByLyrics.html', data = relevant_docs, sbs = 'off', artist = artist_str, album = album_str, year = year_str, page = page)


if __name__ == "__main__":

    # Initalize and trains query completion
    directory = os.getcwd()
    train_csv_file_path = directory + os.sep  + 'sample_lyrics.csv' # Ensure you have `sample_lyrics.csv`
    query_completion = qc.Query_Completion()
    query_completion.train(train_csv_file_path)

    # Execute server
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
