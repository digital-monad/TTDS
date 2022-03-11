# Temporary main Python file for web application routing and Pymongo integration

# Setup Flask and MongoDB - integration for backend and database
from flask import Flask, render_template, request
import configparser, pymongo, os, requests
import QueryParser.parser as qp
import search.preprocess as pp

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'

client = pymongo.MongoClient(uri)

@app.route("/", methods=['GET','POST'])
def show_main_page():
    return render_template('index.html')

def get_songs(advanced_filters, page_size, page_num):

    ids = [4,1,3,2,5,1,2] #TODO: This is a fixed set... Obtain list of ids from Andrew

    try:
        songs_list = list(client.ttds.songMetaData.find(
            {"$and": advanced_filters}
        ))
    except Exception:
        songs_list = list(client.ttds.songMetaData.find())
    
    sorted_song_dict = {d['song_id']: d for d in songs_list}  # sentence_id -> sentence_dict
    sorted_song_list = [sorted_song_dict[i] for i in ids]
    
    sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return sorted_song_list

# Obtain list of relevant songs based on lyrics - TODO: Figure out runtime complexity
def get_songs_based_on_lyrics(advanced_filters, page_size, page_num):
    ids = [4,1,3,2,5,1,2] #TODO: Obtain list of ids from Andrew

    try:
        songs_list = list(client.ttds.songMetaData.find(
            {"$and": advanced_filters}
        ))
    except Exception:
        songs_list = list(client.ttds.songMetaData.find())
    
    sorted_song_dict = {d['song_id']: d for d in songs_list}  # sentence_id -> sentence_dict
    sorted_song_list = [sorted_song_dict[i] for i in ids]
    
    sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return sorted_song_list

ROWS_PER_PAGE = 3 # TODO: SHOULD BE CHANGED

@app.route('/search', methods=['GET', 'POST'])
def display_search_first_results():
    advanced_filters = []
    relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, 1)
    return render_template('search.html', data = relevant_docs)

@app.route('/search/page=<int:page>', methods=['GET', 'POST'])
def display_search_results(page):

    # TODO: Obtain query params for advanced search?
    advanced_filters = []

    if request.args.get('artist', False):
        advanced_filters.append({'artist': request.args.get('artist')})
    if request.args.get('album', False):
        advanced_filters.append({'album': request.args.get('artist')})
    if request.args.get('year', False):
        year_int = int(request.args.get('year'))
        advanced_filters.append({'year': year_int})

    # Checks if script should conduct song search or lyrics search
    try:
        if request.args.get('search-by-songs', False) == 'on':
            relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, page)
        else:
            relevant_docs = get_songs_based_on_lyrics(advanced_filters, ROWS_PER_PAGE, page)
    except Exception:
        relevant_docs = list()
        print('Error retrieving documents')

    return render_template('search.html', data = relevant_docs)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
