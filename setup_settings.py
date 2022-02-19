import configparser

config = configparser.ConfigParser()

config['mongodb'] = {'username': 'group37', 'password': 'ligmaballs-find-the-password-on-msteams-wiki'}
config['geniuslyrics'] = {'genius_client_access_token': 'ligmaballs-find-the-password-on-msteams-wiki'}
config['geniuslyrics_artists_name_letters'] = {'artists_name_letters': 'abcde'}
config['geniuslyrics_data_collection'] = {'data_collection_type': 'sample_data', 'batch_starting_initial': 'a'}
config.write(open('settings.ini', 'w'))
