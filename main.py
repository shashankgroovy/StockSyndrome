import sqlite3
import requests
from contextlib import closing
from flask import Flask, request, jsonify, render_template, g, session, \
        abort, redirect, url_for

# declaring the app
app = Flask(__name__)

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
    #if session['logged_in']:
        #return render_template('mainpage.html')
    return render_template('index.html')


# authentication
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_user(request.form['username'] and request.form['password']):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# get stocks data
@app.route('/data.json', methods=["GET"])
def get_data():
    BASEURL = "http://finance.yahoo.com/d/quotes.csv?s="
    PARAMS = "AAPL+GOOG+MSFT"
    FORMAT = "&f=nsghl1"
    URL = BASEURL + PARAMS + FORMAT
    r = requests.get(URL)
    data = dict()
    lines = r.text
    for l in lines.strip().split('\n'):
        (name, sym, lo, hi, latest) = map(unicode.strip, l.split(","))
        data[sym] = {"name": name, "lo": lo, "hi": hi, "latest": latest}
    return jsonify(data)

# 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()               # Setup the database
    app.secret_key = 'supersecretkey'
    app.run(debug=True)
