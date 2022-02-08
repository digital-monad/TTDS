# Test file to convert original Genius song lyrics called from API in JSON format into CSV format for readability
import csv, json, os

current_path = os.path.dirname(__file__)
file = os.path.normpath(current_path + os.sep + 'sample_data' + os.sep + 'json' + os.sep + 'Test_Lyrics_Eminem.json')

with open(file, encoding='utf-8') as json_file:
    eminem_json_data = json.load(json_file)

json_to_csv_file = os.path.normpath(current_path + os.sep + 'sample_data' + os.sep + 'csv' + os.sep + 'Test_Lyrics_Eminem.csv')

with open(json_to_csv_file, 'w', newline='', encoding='utf-8') as data_file:

    csv_writer = csv.writer(data_file)
    count = 0 # Counter variable used for writing headers to CSV file

    for song_data in eminem_json_data['songs']:
        
        if count == 0:
            # Write headers
            header = ['Song ID','Artist','Title','Album', 'Year', 'Date','Raw Lyrics']
            csv_writer.writerow(header)
            count += 1

        # Write rows
        song_id = count
        artist = eminem_json_data['name']
        title = song_data['title']
        if song_data.get('album') == None:
            album = None
        else:
            album = song_data.get('album').get('name', None)
        release_date = song_data.get('release_date', None)
        if release_date == None:
            year = None
        else:
            year = release_date.split("-")[0]
        raw_lyrics = song_data['lyrics']

        csv_writer.writerow([song_id, artist, title, album, year, release_date, raw_lyrics])
        count += 1