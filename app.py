from flask import Flask, render_template, request, jsonify, session, send_from_directory
import sqlite3
import requests
import random
import urllib.parse
import time
from datetime import datetime

app = Flask(__name__)

#Dictionary of game sessions

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

# helper function returns 5 random songs using iTunes API
def get_artist_songs(artist_name):
    try:
        artist = urllib.parse.quote(artist_name)
        url = f"https://itunes.apple.com/search?term={artist}&media=music&entity=song&limit=10"
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

        return random.sample(songs, min(5, len(songs)))
    
    except Exception as e:
        print(f"Error in get_artist_songs: {str(e)}")
        return []

# creates game session with a unique id and inital game state
def create_game_session(username, artist, songs):

    # get timestamp and create game_id (username + timestamp)
    timestamp = int(time.time())
    game_id = f"{username}_{timestamp}"

    session = {
        "username": username,
        "artist": artist,
        "songs": songs,
        "current_round": 1,
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
    
    game_id, session = create_game_session(username, artist, songs)
    
    first_song = session['songs'][0]
    preview_url = first_song.get('previewUrl', '')
    
    return jsonify({
        "game_id": game_id,
        "round": session['current_round'],
        "total_rounds": session['total_rounds'],
        "artist": session['artist'],
        "preview_url": preview_url,
        "score": 0,
        "message": f"Game started with {artist}!"
    })

# submit guess route
@app.route('/api/submit-guess', methods=['POST'])
def submit_guess():
    try:
        data = request.get_json()
        
        # get game_id and guess from request
        game_id = data.get('game_id')
        guess = data.get('guess')
        
        # validate required fields
        if not game_id or not guess:
            return jsonify({"error": "Missing 'game_id' or 'guess' in request."}), 400
        
        # check if game session exists
        if game_id not in game_sessions:
            return jsonify({"error": f"Game session '{game_id}' not found."}), 404
        
        # get game session data
        game = game_sessions[game_id]
        current_round = game.get('current_round', 1)
        songs = game.get('songs', [])
        score = game.get('score', 0)
        
        # validate round and songs
        if current_round > 3 or current_round < 1:
            return jsonify({"error": "Game has ended or invalid round."}), 400
        
        if not songs or len(songs) < current_round:
            return jsonify({"error": "No songs available for this round."}), 500
        
        # get current song for this round
        current_song = songs[current_round - 1]
        correct_answer = current_song.get('trackName', '')
        
        # check if guess is correct (case-insensitive)
        is_correct = guess.lower().strip() == correct_answer.lower().strip()
        
        # update score if correct
        if is_correct:
            score += 10
            game_sessions[game_id]['score'] = score
        
        # prepare response
        response = {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "round": current_round,
            "score": score,
            "preview_url": current_song.get('previewUrl', ''),
            "message": f"Round {current_round} of 3"
        }
        
        # move to next round
        next_round = current_round + 1
        if next_round <= 3:
            game_sessions[game_id]['current_round'] = next_round
            response["message"] = f"Round {next_round} of 3"
        else:
            # game finished
            response["message"] = "Game completed!"
            # optionally save final score to database here
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in /api/submit-guess: {str(e)}")
        return jsonify({"error": str(e)}), 500

# test route to check game sessions
@app.route('/api/game-sessions', methods=['GET'])
def get_game_sessions():
    try:
        return jsonify({
            "active_sessions": len(game_sessions),
            "sessions": {k: {
                "username": v.get("username"),
                "artist": v.get("artist"),
                "current_round": v.get("current_round"),
                "score": v.get("score")
            } for k, v in game_sessions.items()}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    #add_data()
    app.run(debug=True, use_reloader=False)

    