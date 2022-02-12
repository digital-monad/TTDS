import os, time, logging, configparser
import lyricsgenius as lg

lettersSet = [c for c in "abcde"]

current_path = os.path.dirname(__file__)
settings_file = os.path.normpath(
    current_path + os.pardir.join([os.sep]*4) + 'settings.ini'
)

logging.basicConfig(filename='data_collection.log', encoding='utf-8', level=logging.INFO)

config = configparser.ConfigParser()
config.read(settings_file)
genius_lyrics_client_access_token = config.get('geniuslyrics', 'genius_client_access_token')

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

                artist_data.save_lyrics()
                # If lyrics save successful
                logging.info(f"Successfully wrote lyrics for {line}")
                artists_scraped.add(artist)
    except:
        logging.warning("Ran into either HTTP error or Timeout")
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