import os, time, logging, configparser, requests
import lyricsgenius as lg

current_path = os.path.dirname(__file__)
settings_file = os.path.normpath(
    current_path + os.pardir.join([os.sep]*4) + 'settings.ini'
)


config = configparser.ConfigParser()
config.read(settings_file)
genius_lyrics_client_access_token = config.get('geniuslyrics', 'genius_client_access_token')

artists_name_initial_letters = config.get('geniuslyrics_artists_name_letters', 'artists_name_letters')
lettersSet = [c for c in artists_name_initial_letters]

logging.basicConfig(filename='data_collection' + "".join(lettersSet) + '.log', encoding='utf-8', level=logging.INFO)


def scrapeLetter(letter):
    artists_file = os.path.normpath(current_path + os.sep + os.pardir + os.sep + 'albums_text' + os.sep + "artists_" + l)
    artists_scraped = set()
    genius = lg.Genius(genius_lyrics_client_access_token, 
                   skip_non_songs=True, 
                   excluded_terms=["remix", "live"], # Exclude live and remix versions
                   remove_section_headers=True,
                   timeout=600,
                   retries=10)
    try:
        with open(artists_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                logging.info(f"Searching songs by {line}")
                artist = line.strip()
                artist_data = genius.search_artist(artist, include_features=True) # TODO: CHANGE THE MAX_SONGS

                artist_data.save_lyrics(overwrite=True)
                # If lyrics save successful
                logging.info(f"Successfully wrote lyrics for {line}")
                print(f"Succesfully wrote lyrics for {line}")
                artists_scraped.add(artist)
    
    except Exception as e:
        print("Ran into an HTTP or Timeout error - pausing and retrying")
        logging.warning(e)
        # Remove the already scraped artists from the file
        with open(artists_file, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip() not in artists_scraped:
                    file.write(line)

        time.sleep(30)
        logging.info("Pausing for 30 seconds before retrying")
        # Re-run the same logic with the refreshed file
        scrapeLetter(letter)

for l in lettersSet:
    logging.info(f"Searching for artists beginning with '{l}'")
    scrapeLetter(l)
logging.info(f"SUCCESS!! All lyrics successfully scraped")
