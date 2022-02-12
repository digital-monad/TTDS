import configparser

config = configparser.ConfigParser()

config['mongodb'] = {'username': 'group37', 'password': 'ligmaballs-find-the-password-on-msteams-wiki'}
config['geniuslyrics'] = {'genius_client_access_token': 'ligmaballs-find-the-password-on-msteams-wiki'}
config['geniuslyrics_artists_name_letter'] = {'artist_name_letter': 'artists_a'}
config.write(open('settings.ini', 'w'))