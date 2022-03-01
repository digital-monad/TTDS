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

@app.route("/", methods=['GET','POST'])
def show_main_page():
    return render_template('index.html')

# PyMongo Pagination - TODO: Figure out runtime complexity
def get_relevant_docs(page_size, page_num):
    skips = page_size * (page_num - 1) # Calculate num of docs to skip

    client = pymongo.MongoClient(uri)
    genius_lyrics_data_documents = client.ttds.geniusLyrics.find().skip(skips).limit(page_size) # TODO - find more efficient way

    return genius_lyrics_data_documents

# SIMPLIFIED VERSION - must parse query and conduct ranking from python parsing module before rendering template

## TODO: Create default search which just shows first page
@app.route('/search', methods=['GET', 'POST'])
def display_search_first_results():
    client = pymongo.MongoClient(uri)
    genius_lyrics_data_documents = client.ttds.geniusLyrics.find()
    return render_template('search.html', data = genius_lyrics_data_documents)

ROWS_PER_PAGE = 1 # SHOULD BE CHANGED
@app.route('/search/page=<int:page>', methods=['GET', 'POST'])
def display_search_results(page):
    query = request.form.get('q')

    bs_parser = qp.BooleanSearchParser()
    bs_parser.query(query) # Parse query - determine what algorithm to use
    #print(bs_parser.query(query))

    # TODO: obtain correct function for search by lyrics
    #pre_processed_song_lyrics = pp.preprocessSongLyrics(query)
    #print(pre_processed_song_lyrics)
    
    # TODO: get index from

    genius_lyrics_data = get_relevant_docs(ROWS_PER_PAGE, page)
    return render_template('search.html', data = genius_lyrics_data)

#TODO: Get movie id - requires individual page
