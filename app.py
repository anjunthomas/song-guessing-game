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

#@app.route('/test', methods=['POST'])
#def test_route():
#    data = request.get_json()
#    name = data.get("name", "Guest")
    
#    return jsonify({
#        "message": f"Hello, {name}! Your request was received successfully."
#    })
###

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

# helper function to save score to database
def save_score_to_db(username, score, artist):
    """
    Save a game score to the database
    Returns True if successful, False if error
    """
    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        cursor.execute('''
            INSERT INTO scores (username, score, artist) 
            VALUES (?, ?, ?)
        ''', (username, score, artist))
        
        connection.commit()
        connection.close()
        print(f"Score saved: {username} - {score} points ({artist})")
        return True
        
    except Exception as e:
        print(f"Error saving score: {str(e)}")
        return False

# helper function returns up to 5 random songs using iTunes API
def get_artist_songs(artist_name):
    try:
        artist = urllib.parse.quote(artist_name)
        url = f"https://itunes.apple.com/search?term={artist}&media=music&entity=song&limit=10"
        response = requests.get(url)

        # check if request worked
        if response.status_code != 200:
            return []

        data = response.json()
        results = data.get("results", [])

        # initialize song array
        songs = []
        artist_name_lower = artist_name.lower()

        # append songs with "previewUrl" key
        # exclude songs with artist name in fields other than "artistName"
        # exlude songs with "ft" or "feat"
        for song in results:
            if ("previewUrl" in song and 
            song.get("artistName", "").lower() == artist_name_lower and
            not any (ft in song.get("trackName", "").lower() for ft in ["ft", "feat"])
            ):
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

    round_limit = min(5, len(songs))

    session = {
        "username": username,
        "artist": artist,
        "songs": songs[:round_limit],
        "current_round": 1,
        "total_rounds": round_limit,
        "score": 0,
        "max_guesses": 3,
        "guesses_remaining": 3
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
        "message": f"Game started with {artist}!",
        "guesses_remaining": session['guesses_remaining']
    })

# submit guess route
@app.route('/api/submit-guess', methods=['POST'])
def submit_guess():
    try:
        data = request.get_json()
        
        # get game_id and guess from request
        game_id = data.get('game_id')
        guess = data.get('guess')
        is_timeout = guess == ""
        
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
        round_limit = min(game.get('total_rounds', len(songs)), 5)
        max_guesses = game.get('max_guesses', 3)
        guesses_remaining = game.get('guesses_remaining', max_guesses)

        # ensure guesses_remaining is tracked
        if 'guesses_remaining' not in game:
            game_sessions[game_id]['guesses_remaining'] = guesses_remaining

        # validate round and songs
        if current_round > round_limit or current_round < 1:
            return jsonify({"error": "Game has ended or invalid round."}), 400

        if not songs or len(songs) < current_round:
            return jsonify({"error": "No songs available for this round."}), 500

        # get current song for this round
        current_song = songs[current_round - 1]
        correct_answer = current_song.get('trackName', '')

        # check if guess is correct (case-insensitive)
        is_correct = guess.lower().strip() == correct_answer.lower().strip()

        # track state for response
        advance_round = False
        game_over = False
        next_round = current_round
        next_preview_url = current_song.get('previewUrl', '')
        message = ""
        round_for_response = current_round

        if is_correct:
            score += 10
            game_sessions[game_id]['score'] = score
            advance_round = True
            message = "Correct!"
        else:
            guesses_remaining -= 1
            game_sessions[game_id]['guesses_remaining'] = guesses_remaining

            if guesses_remaining > 0:
                message = f"Incorrect. {guesses_remaining} guesses remaining."
            else:
                advance_round = True
                message = "No guesses remaining."

        if advance_round:
            next_round = current_round + 1
            has_next_song = next_round <= round_limit and len(songs) >= next_round

            if has_next_song:
                game_sessions[game_id]['current_round'] = next_round
                game_sessions[game_id]['guesses_remaining'] = max_guesses
                next_preview_url = songs[next_round - 1].get('previewUrl', '')
                message = message + f" Moving to round {next_round}."
                guesses_remaining = max_guesses
                round_for_response = next_round
            else:
                # game finished - save final score to database
                username = game.get('username', 'Unknown')
                artist = game.get('artist', 'Unknown')

                if save_score_to_db(username, score, artist):
                    message = message + " Game completed! Score saved to leaderboard."
                else:
                    message = message + " Game completed! (Note: Score saving failed)"

                game_over = True
                guesses_remaining = 0
                next_preview_url = ''
                round_for_response = round_limit

        # prepare response object using updated values
        response = {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "round": round_for_response,
            "score": score,
            "preview_url": next_preview_url,
            "message": message.strip(),
            "guesses_remaining": guesses_remaining,
            "artist_name": current_song.get('artistName', ''),
            "album_name": current_song.get('collectionName', ''),
            "album_cover": current_song.get('artworkUrl100', '')
        }

        if game_over:
            # remove game session from memory to free up space
            if game_id in game_sessions:
                del game_sessions[game_id]

        return jsonify(response)
        
    except Exception as e:
        print(f"Error in /api/submit-guess: {str(e)}")
        return jsonify({"error": str(e)}), 500

# fetch current round details without mutating game state
@app.route('/api/next-round', methods=['GET'])
def get_next_round():
    try:
        game_id = request.args.get('game_id')

        if not game_id:
            return jsonify({"error": "Missing 'game_id' query parameter."}), 400

        if game_id not in game_sessions:
            return jsonify({"error": f"Game session '{game_id}' not found."}), 404

        game = game_sessions[game_id]
        songs = game.get('songs', [])
        current_round = game.get('current_round', 1)
        total_rounds = game.get('total_rounds', len(songs))
        score = game.get('score', 0)
        guesses_remaining = game.get('guesses_remaining', game.get('max_guesses', 3))

        if total_rounds == 0 or not songs:
            return jsonify({"error": "No songs available for this game session."}), 400

        # If the session has progressed past available songs, treat as game over
        if current_round > total_rounds:
            return jsonify({
                "round": total_rounds,
                "total_rounds": total_rounds,
                "artist": game.get('artist', ''),
                "preview_url": "",
                "score": score,
                "guesses_remaining": 0,
                "message": "Game completed."
            })

        current_song = songs[current_round - 1]
        preview_url = current_song.get('previewUrl', '')

        return jsonify({
            "round": current_round,
            "total_rounds": total_rounds,
            "artist": game.get('artist', ''),
            "preview_url": preview_url,
            "score": score,
            "guesses_remaining": guesses_remaining
        })

    except Exception as e:
        print(f"Error in /api/next-round: {str(e)}")
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

    