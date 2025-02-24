from flask import Flask,request,render_template,redirect,session
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
import os

app=Flask(__name__)
app.secret_key=os.urandom(24)

db_file="Voting_System.db"

def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor=conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        has_voted INTEGER DEFAULT 0
        )
    ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate TEXT
        
        )


    ''')

@app.route("/")
def index():
    if 'user' in session:
        return redirect('/vote')
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",(username,password))
                conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already exists."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                session['user'] = username
                return redirect('/vote')
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user' not in session:
        return redirect('/login')
    username = session['user']
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT has_voted FROM users WHERE username = ?", (username,))
        has_voted = cursor.fetchone()[0]
        if has_voted:
            return "You have already voted!"
        if request.method == 'POST':
            candidate = request.form['candidate']
            cursor.execute("INSERT INTO votes (candidate) VALUES (?)", (candidate,))
            cursor.execute("UPDATE users SET has_voted = 1 WHERE username = ?", (username,))
            conn.commit()
            return "Vote cast successfully!"
    return render_template('vote.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)