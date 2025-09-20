from flask import Flask, render_template, request, jsonify, session, send_from_directory
import sqlite3
import requests
import random
import urllib.parse

app = Flask(__name__)

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

    cursor.execute('INSERT INTO scores (username, score, artist) VALUES (?, ?, ?)', ("bob", 2, "Ariana Grande"))

    connection.commit()
    connection.close()


if __name__ == '__main__':
    init_db()
    add_data()
    app.run(debug=True, use_reloader=False)

    