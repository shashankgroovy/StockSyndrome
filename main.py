import sqlite3
import requests
from flask import Flask, request, jsonify, render_template

# database
#database = 'users.db'

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

#@app.route('/stocks.json', methods=["GET"])
#def get_stocks():
    #pass

if __name__ == '__main__':
    app.run()
