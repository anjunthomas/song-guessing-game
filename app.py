from flask import Flask, render_template, request, jsonify, session, send_from_directory
import sqlite3
import requests
import random
import urllib.parse
from datetime import datetime

app = Flask(__name__)

# dicitonary of game sessions
game_sessions = {}

@app.route('/')
def index(): 
    return send_from_directory('static', 'index.html')

#backend developers, create a new route here with your name that returns a similar message
# Ex route. '/anju' 
# push to your branch to verify flask is working

#example route to show POST request 
@app.route('/test', methods=['POST'])
def test_route():
    data = request.get_json()
    name = data.get("name", "Guest")
    
    return jsonify({
        "message": f"Hello, {name}! Your request was received successfully."
    })

# thaira's personal route following example above
@app.route('/thaira')
def thaira():
    return "Hello, my name is Thaira!"

# jessie's personal route following example above
@app.route('/jessie')
def jessie():
    return "Hello, my name is Jessie!"

# game route
@app.route('/game', methods=['POST'])
def game():
    return jsonify({
        "message": "game route is working"
    })

# api scores route
@app.route('/api/scores', methods=['GET'])
def get_scores():
    try:
        # establish database connection
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        # query to get top 10 scores ordered by score (highest first)
        # removed timestamp from query since column might not exist yet
        cursor.execute('''
            SELECT username, score, artist 
            FROM scores 
            ORDER BY score DESC 
            LIMIT 10
        ''')
        
        # get the scores
        scores = cursor.fetchall()
        print(f"Found {len(scores)} scores in database")  # Debug info
        
        # initialize leaderboard array
        leaderboard = []
        
        # append all usernames, scores, and artist names to the leaderboard
        for score in scores:
            leaderboard.append({
                "username": score[0],
                "score": score[1], 
                "artist": score[2]
            })
        
        connection.close()
        
        # return the leaderboard in JSON form
        return jsonify(leaderboard)
        
    except Exception as e:
        print(f"Error in /api/scores: {str(e)}")  # Debug info
        return jsonify({"error": str(e)}), 500

# test database connection route
@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(scores)")
        columns = cursor.fetchall()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM scores")
        count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute("SELECT * FROM scores LIMIT 3")
        sample = cursor.fetchall()
        
        connection.close()
        
        return jsonify({
            "message": f"Database connected! Found {count} scores.",
            "columns": [col[1] for col in columns],  # column names
            "sample_data": sample,
            "full_column_info": columns
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# initialize database
def init_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER,
            artist TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    connection.commit()
    connection.close()


def add_data():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO scores (username, score, artist) VALUES (?, ?, ?)', ("lisa", 3, "Doja Cat"))

    connection.commit()
    connection.close()

# helper function returns 3 random songs using iTunes API
def get_artist_songs(artist_name):
    try:
        artist = urllib.parse.quote(artist_name)
        url = f"https://itunes.apple.com/search?term={artist}&media=music&entity=song&limit=5"
        response = requests.get(url)

        # check if request worked
        if response.status_code != 200:
            return[]

        data = response.json()
        results = data.get("results", [])

        # initialize song array
        songs = []

        # append songs with "previewUrl" key
        for song in results:
            if "previewUrl" in song:
                songs.append(song)

        return random.sample(songs, min(3, len(songs)))
    
    except Exception as e:
        print(f"Error in get_artist_songs: {str(e)}")
        return []

# creates game session with a unique id and inital game state
def create_game_session(username, artist, songs):

    # get timestamp and create game_id (username + timestamp)
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    game_id = f"{username}_{timestamp}"

    session = {
        "username": username,
        "artist": artist,
        "songs": songs,
        "start_round": 1,
        "total_rounds": len(songs),
        "score": 0
    }

    # add session dict into global game_sessions
    # unique game session can be accessed via game_id
    game_sessions[game_id] = session
    return game_id, session

# start game route
@app.route('/api/start-game', methods = ['POST'])
def start_game():
    data = request.get_json()

    # get username and artist from request
    username = data.get('username')
    artist = data.get('artist')

    # check if both values exist
    if not username or not artist:
        return jsonify({"error": "Missing 'username' or 'artist' in request."}), 400
    
    try:
        # call helper function to fetch songs
        songs = get_artist_songs(artist)

    except Exception as e:
        return jsonify({"error": f"Error fetching songs: {str(e)}"}), 500
    
    if not songs:
        return jsonify({"error": f"No songs found for artist '{artist}'."}), 404
    
    # call helper function to create session
    game_id, session = create_game_session(username, artist, songs)

    # get first song's preview URL
    first_song = session['songs'][0]
    preview_url = first_song.get('previewUrl', '')

    return jsonify({
        "game_id": game_id,
        "round": session['start_round'],
        "total_rounds": session['total_rounds'],
        "artist": session['artist'],
        "preview_url": preview_url,
        "score": 0,
        "message": f"Game started with {artist}!"
    })

if __name__ == '__main__':
    init_db()
    add_data()
    app.run(debug=True, use_reloader=False)

    