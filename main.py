# Temporary main Python file for web application routing and Pymongo integration

# Setup Flask and MongoDB - integration for backend and database
from flask import Flask, render_template, request
import configparser, pymongo, os, requests
# NOTE: QueryParser library to be fixed by Andrew
#from QueryParser import QueryParser as qp 
#from Querying import preprocess as pp

app = Flask(__name__)

#QueryParserClass = qp.QueryParser()

####### TO BE REFACTORED? ##########
config = configparser.ConfigParser()
config.read('settings.ini')
base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri)
####### TO BE REFACTORED? ##########


@app.route("/", methods=['GET','POST'])
def show_main_page():
    return render_template('index.html')

# Feature: SEARCH BY SONGS
def get_songs(advanced_filters, page_size, page_num):

    # Obtain query
    song_name = ''
    isSong = True
    if request.args.get('q'):
        song_name = request.args.get('q')
    #query = QueryParserClass.query(song_name, isSong)

    #TODO: This is a fixed set from songs by Eminem made in 2013
    # Obtain list of song_ids ordered from Andrew
    song_ids = ["1158679", "1158688", "1158655", "1158651", "1158652", "1158664", "1158673"] 
    
    # TODO: Determine final limit for querying results back to front-end
    try:
        songs_list = list(client.ttds.songMetaData
            .find(
                    {"_id": { "$in": song_ids }},
                    {"$and": advanced_filters}
                )
            .limit(100)
        )
    
    # Handling w/out advanced features included
    except Exception:
        songs_list = list(client.ttds.songMetaData
            .find({"_id": { "$in": song_ids }})
            .limit(100)
        )

    #print("This is the songs list")
    #print(songs_list)
    
    sorted_song_dict = {d['_id']: d for d in songs_list}  # sentence_id -> sentence_dict
    
    # Obtain new list of ORDERED ids - allow advanced search
    new_ids = []
    for id in song_ids:
        if id in sorted_song_dict:
            new_ids.append(id)

    sorted_song_list = [sorted_song_dict[i] for i in new_ids]
    
    new_sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return new_sorted_song_list

# Feature: SEARCH BY SONG LYRICS - join collections together
def get_songs_based_on_lyrics(advanced_filters, page_size, page_num):

    # Obtain query
    lyrics_expr = ''
    isSong = False
    if request.args.get('q'):
        lyrics_expr = request.args.get('q')
    #query = QueryParserClass.query(song_name, isSong)

    #TODO: This is a fixed set from songs by Eminem made in 2013
    # Obtain list of lyrics line_ids ordered from Andrew
    lyrics_ids = ["0", "1", "2", "3", "4", "5", "6"] # Currently no constraints

    # TODO: Aggregate lyricMetaData for songMetaData
    # Determine final limit for querying results back to front-end
    try:
        lyrics_list = list(client.ttds.lyricMetaData
            .find(
                    {"_id": { "$in": lyrics_ids }},
                )
            .limit(100)
        )
    
    # Handle w/out advanced features included
    except Exception:
        lyrics_list = list(client.ttds.lyricMetaData
            .find(
                    {"_id": { "$in": lyrics_ids }},
                )
            .limit(100)
        )
    
    sorted_lyric_dict = {d['_id']: d for d in lyrics_list}  # sentence_id -> sentence_dict

    # Obtain new list of ORDERED ids - allow advanced search
    new_ids = []
    for id in lyrics_ids:
        if id in sorted_lyric_dict:
            new_ids.append(id)

    sorted_lyrics_list = [sorted_lyric_dict[i] for i in new_ids]
    
    new_sorted_lyrics_list = sorted_lyrics_list[(page_num - 1) * page_size : page_num * page_size]

    return new_sorted_lyrics_list

ROWS_PER_PAGE = 3 # TODO: SHOULD BE CHANGED

@app.route('/search', methods=['GET', 'POST'])
def display_search_first_results():
    advanced_filters = []
    relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, 1)
    return render_template('search.html', data = relevant_docs)

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
    else:
        relevant_docs = get_songs_based_on_lyrics(advanced_filters, ROWS_PER_PAGE, page)

    return render_template('search.html', data = relevant_docs, sbs = 'on', artist = artist_str, album = album_str, year = year_str, page = page)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
