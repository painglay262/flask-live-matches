# Flask Live Matches API

This is a Flask-based API that fetches live football match data from an external JSON source.

## Features
- Fetches match details including teams, league, and match time
- Detects whether a match is live
- Retrieves M3U8 streaming URLs for live matches
- Ready for deployment on **Render**

## Installation
```sh
git clone https://github.com/painglay262/flask-live-matches.git
cd flask-live-matches
pip install -r requirements.txt
python app.py