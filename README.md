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
