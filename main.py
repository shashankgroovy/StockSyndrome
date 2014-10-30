import os
import sqlite3
import requests
from contextlib import closing
from flask import Flask, request, jsonify, render_template, g, session, \
        abort, redirect, url_for
from flask.ext.triangle import Triangle


app = Flask(__name__, static_path='/static')
Triangle(app)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'users.db'),
    DEBUG=True,
    SECRET_KEY='supersecretkey',
))


# database configurations and methods
users_db = 'users.db'

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(users_db)
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.execute("INSERT INTO `users` (`username`, `password`, `email`) \
                       VALUES ('admin', 'password', 'email@mail.com')")
            db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



# views
@app.route('/', methods=["GET"])
def index():
    try:
        if session['logged_in']:
            return render_template('mainpage.html')
    except KeyError:
        pass
    return render_template('index.html')


# authentication
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    db = connect_db()
    cursor = db.cursor()
    try:
        if session['logged_in']:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            if username and password and email:
                try:
                    query = "INSERT INTO `users` (`username`, `password`, `email`) VALUES (?, ?, ?)"
                    cursor.execute(query, (username, password, email))
                    db.commit()
                    flash('You have successfully created an account')
                    session['logged_in'] = True
                    return redirect(url_for('index'))
                except:
                    pass
            else:
                error = 'Invalid credentials'
    except KeyError:
            return render_template('signup.html', error=error)
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = connect_db()
    cursor = db.cursor()
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            try:
                query = "SELECT * FROM `users` WHERE `username` = ? AND `password` = ?"
                cursor.execute(query, (username, password))
                results = cursor.fetchall()
                #print results[0][0]
                if not results:
                    error = "Invalid username/password"
                    return render_template('login.html', error=error)
                session['logged_in'] = True
                return redirect(url_for('index'))
            except db.Error:
                error = 'Invalid arguments'
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
    markets = ['AAPL', 'GOOG', 'MSFT', 'YHOO', 'TWTR', 'FB', 'TSLA', 'IBM', 'DELL', 'NOK', 'ADBE', 'AOL', 'KO', 'F', 'JNJ', 'T', 'GM', 'INTC', 'GRPN', 'CSCO', 'VZ']
    market = ['AAPL', 'GOOG', 'MSFT',]

    BASEURL = "http://finance.yahoo.com/d/quotes.csv?s="
    STOCK = "+".join(market)
    FORMAT = "&f=nsghl1"
    URL = BASEURL + STOCK + FORMAT
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
