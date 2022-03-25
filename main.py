# Temporary main Python file for web application routing and Pymongo integration

# Setup Flask and MongoDB - integration for backend and database
from flask import Flask, render_template, request
import configparser, pymongo, os, requests
import Querying.QueryParser as qp
import Querying as preprocess
import requests

app = Flask(__name__)

queryParser = qp.QueryParser()

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

# Obtain list of relevant songs
def get_songs(advanced_filters, page_size, page_num):

    print("here")
    parsed = str(queryParser.parseQuery('#(10,proximity,search)', True))

    try:

        res = requests.get('http://127.0.0.1:8000/query?query='+str(parsed))

    except:

        print("exception")

        raise BaseException("testing")

    parsed = str(queryParser.parseQuery('"phrase"', True))

    try:

        res = requests.get('http://127.0.0.1:8000/query?query='+str(parsed))

    except:

        print("exception")

        raise BaseException("testing")

    parsed = str(queryParser.parseQuery('ranked', True))

    try:

        res = requests.get('http://127.0.0.1:8000/query?query='+str(parsed))

    except:

        print("exception")

        raise BaseException("testing")

    print(res.content)

    raise BaseException("testing")


    try:
        songs_list = list(client.ttds.songMetaData.find(
            {"$and": advanced_filters}
        ))
    except Exception:
        songs_list = list(client.ttds.songMetaData.find())
    
    sorted_song_dict = {d['song_id']: d for d in songs_list}  # sentence_id -> sentence_dict
    
    # Obtain new list of ORDERED ids - allow advanced search
    new_ids = []
    for id in ids:
        if id in sorted_song_dict:
            new_ids.append(id)

    sorted_song_list = [sorted_song_dict[i] for i in new_ids]
    
    new_sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return new_sorted_song_list

# Obtain list of relevant songs based on lyrics
def get_songs_based_on_lyrics(advanced_filters, page_size, page_num):


    parsed = queryParser.parseQuery('"test" && spiderman')

    try:

        res = requests.get('http://127.0.0.1:8000/query?query='+str(parsed))

    except:

        print("exception")

        return 

    print(res.content)

    return

    try:
        songs_list = list(client.ttds.songMetaData.find(
            {"$and": advanced_filters}
        ))
    except Exception:
        songs_list = list(client.ttds.songMetaData.find())
    
    sorted_song_dict = {d['song_id']: d for d in songs_list}  # sentence_id -> sentence_dict

    # Obtain new list of ORDERED ids - allow advanced search
    new_ids = []
    for id in ids:
        if id in sorted_song_dict:
            new_ids.append(id)

    sorted_song_list = [sorted_song_dict[i] for i in new_ids]
    
    new_sorted_song_list = sorted_song_list[(page_num - 1) * page_size : page_num * page_size]

    return new_sorted_song_list

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

    # Checks if script should conduct song search or lyrics search
    try:
        
        relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, page)

        # Was getting an error so just checked over song search  \/

        # if request.args.get('search-by-songs', False) == 'on':
        #     relevant_docs = get_songs(advanced_filters, ROWS_PER_PAGE, page)
        # else:
        #     relevant_docs = get_songs_based_on_lyrics(advanced_filters, ROWS_PER_PAGE, page)
    except Exception:

        relevant_docs = list()
        print('Error retrieving documents')

    return render_template('search.html', data = relevant_docs, artist = artist_str, album = album_str, year = year_str, page = page)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
