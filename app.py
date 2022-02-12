# Temporary setup for application - will be divided up later

# Setup Flask and MongoDB - integration for backend and database
from flask import Flask, render_template
import configparser, pymongo, os

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('settings.ini')

base_uri = 'mongodb+srv://'
username = config.get('mongodb', 'username')
password = config.get('mongodb', 'password')
uri = base_uri + username + ':' + password + '@ttds-group-37.0n876.mongodb.net/ttds?retryWrites=true&w=majority'

@app.route("/")
def show_main_page():
    client = pymongo.MongoClient(uri)
    genius_lyrics_data = list(client.ttds.geniusLyrics.find())
    return render_template('index.html', data = genius_lyrics_data)

