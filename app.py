from flask import Flask, render_template, request, jsonify, session, send_from_directory
import sqlite3
import requests
import random
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index(): 
    return send_from_directory('static', 'index.html')


@app.route('/jessie')
def jessie():
    return "Hi this is Jessie"
#backend developers, create a new route here with your name that returns a similar message
# Ex route. '/anju' 
# push to your branch to verify flask is working


if __name__ == '__main__':
    init_db()
    add_data()
    app.run(debug=True, use_reloader=False)

    