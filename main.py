import sqlite3
import requests
from flask import Flask, request, jsonify, render_template, g
from contextlib import closing

# declaring the app
app = Flask(__name__)
DEBUG = True

# create db
users_db = 'users.db'

def connect_db():
    return sqlite3.connect(users_db)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# database setup and teardown
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# views
@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')

@app.route('/stocks.json', methods=["GET"])
def get_stocks():
    pass

# authentication
@app.route('/login', methods=['GET', 'SET'])
def login():
    if request.method == 'POST':
        do_login()
    else:
        return render_template('login.html')

if __name__ == '__main__':
    init_db()               # Setup the database
    app.run()               # Go live!!!
