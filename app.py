from flask import Flask, render_template, request, jsonify, session, send_from_directory
import sqlite3
import requests
import random
import urllib.parse

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World, this is the song guessing game made by Anju!"

#backend developers, create a new route here with your name that returns a similar message
# Ex route. '/anju' 
# push to your branch to verify flask is working


if __name__ == '__main__':
    app.run(debug=True)

    