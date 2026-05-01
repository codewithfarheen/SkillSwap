from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"  # needed for session

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        skill_id INTEGER
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                       (name,email,password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                       (email,password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['user_id'] = user[0]   # store user
            return redirect('/dashboard')
        else:
            error = "Invalid login"

    return render_template('login.html', error=error)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ---------------- POST SKILL ----------------
@app.route('/post-skill', methods=['GET','POST'])
def post_skill():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO skills (user_id,title,description) VALUES (?,?,?)",
                       (session['user_id'],title,description))

        conn.commit()
        conn.close()

        return redirect('/skills')

    return render_template('post_skill.html')

# ---------------- VIEW SKILLS ----------------
@app.route('/skills')
def skills():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()

    # get requested skills for current user
    cursor.execute("SELECT skill_id FROM requests WHERE sender_id=?",
                   (session['user_id'],))
    requested = [r[0] for r in cursor.fetchall()]

    conn.close()

    return render_template('skills.html', skills=skills, requested=requested)

# ---------------- REQUEST SKILL ----------------
@app.route('/request/<int:skill_id>', methods=['POST'])
def request_skill(skill_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # check if already requested
    cursor.execute("SELECT * FROM requests WHERE sender_id=? AND skill_id=?",
                   (session['user_id'], skill_id))
    already = cursor.fetchone()

    if not already:
        cursor.execute("INSERT INTO requests (sender_id, skill_id) VALUES (?,?)",
                       (session['user_id'], skill_id))
        conn.commit()

    conn.close()

    return redirect('/skills')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)