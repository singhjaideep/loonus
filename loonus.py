#import stuff
import sqlite3, string, random
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
#configuration
DATABASE = '/tmp/loonus.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create app
app = Flask(__name__)
app.config.from_object(__name__)

#db functions
def connect_db():
	return sqlite3.connect(app.config["DATABASE"])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select original, shorturl from entries order by id desc')
    entries = [dict(original=row[0], shorturl='loon.us/'+row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

def shorturlcalc(originalurl):
	letterarray = string.ascii_uppercase + string.ascii_lowercase + string.digits
	return ''.join(random.SystemRandom().choice(letterarray) for _ in range(6))

@app.route('/add', methods=['POST'])
def add_entry():
    su = shorturlcalc(request.form['original'])
    g.db.execute('insert into entries (original, shorturl) values (?, ?)',[request.form['original'], su])
    g.db.commit()
    flash('New tinyurl created')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    session['logged_in'] = True
    flash('You were logged in')
    return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
	app.run(debug=True)