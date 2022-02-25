# TTDS Coursework 3
Group coursework for the Text Technologies for Data Science course.

## Overview
- Frontend: No framework needed (unless if additional time allows) 
- Backend: Python 3.9.5 + Flask
- DB: MongoDB
- Git Version Control

# Team Software Practices
- Create own branch and push it into your own branch
- Create a Pull Request on GitHub and request for a reviewer
- 1 Reviewer should review your code; if approved - it should be then merged into main branch

## Local Host Setup (Anaconda)
1. `conda env create -f environment.yml`
2. To configure settings file, type in: `python setup_settings.py`
3. Go to `settings.ini` file and update password - refer to MSTeams Wiki if needed
    - This is absolutely needed to prevent freely exposing API keys and passwords
4. Install MongoDB Compass for better visualization

## Local Host Setup
1. Ensure MongoDB is installed on your computer
2. Install MongoDB Compass for better visualization
3. Install Flask / Ensure Flask is installed
    - [ ] Ensure you are in the correct directory of the project folder
    - For Windows users use PowerShell:
        - [ ] `py -3 -m venv venv`
        - [ ] `venv\Scripts\activate`
        - [ ] `pip install Flask`
    - For Mac/Linux users use Terminal:
        - [ ] `python3 -m venv venv`
        - [ ] `. venv/bin/activate`
        - [ ] `pip install Flask`
    - Please ensure you have Python version 3.9.5 (should be fine tho)
4. Install following dependencies
    - [ ] `pip install pymongo`
    - [ ] `pip install dnspython`
5. To configure settings file, type in: `python setup_settings.py`
6. Go to `settings.ini` file and update - please refer to MSTeams Wiki if needed
    - This is absolutely needed to prevent freely exposing API keys and passwords

## Executing Server
1. Ensure your virtual environment is already setup properly
2. Type the following in your console: `./run`

## Data Collection

### Translating JSON to CSV files]
**NOTE**: Lyrics greater than 20000 characters will not be transferred - due to CSV ability to write up to 32k characters.
In addition most likely a play rather than an actual song

1. Assuming `settings.ini` is already setup, go to the `geniuslyrics_datacollection` section
and change `data_collection_type` option value along with `batch_starting_initial` option value
- NOTE: `data_collection_type` can either be `sample_data` or `test_data`
- NOTE: `batch_starting_initial` can be from folder a to z but the initial name must be clearly defined
2. Create a folder under `test_data` called `csv`
3. Test_Data folder should not contain JSON files and should be stored in either local host or Microsoft Teams or OneDrive
    - Reduce file transfer size
4. CSVs however must be transferred and shown in GitHub repo
