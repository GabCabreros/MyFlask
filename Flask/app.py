from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = '12345'

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            userName VARCHAR(50),
            userPassword VARCHAR(50)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            idno INTEGER PRIMARY KEY,
            name VARCHAR(50),
            course VARCHAR(50),
            level VARCHAR(50)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data to log the user out
    session.clear()  # This clears all session variables
    return redirect(url_for('login'))  # Redirect the user to the login pag

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE userName = ? AND userPassword = ?', (username, password)).fetchone()
        students = conn.execute('SELECT * FROM students').fetchall()
        conn.close()

        if user:
            session['username'] = username  # Save user in session
            return redirect(url_for('success'))  # Redirect after POST to prevent resubmission
        else:
            return "Login failed. Invalid username or password."

    return render_template('index.html')

@app.route('/success')
def success():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # render template with student list
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('sucessLogin.html', username=session['username'], students=students)

@app.route('/delete/<int:idno>', methods=['POST'])
def delete(idno):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE idno = ?', (idno,))
    conn.commit()
    conn.close()
    return redirect(url_for('success'))

@app.route('/addstudent', methods=['POST'])
def addstudent():
    idno = request.form.get('idno')
    name = request.form.get('name')
    course = request.form.get('course')
    level = request.form.get('level')

    if not all([idno, name, course, level]):
        return "All fields are required.", 400

    conn = get_db_connection()
    conn.execute('INSERT INTO students (idno, name, course, level) VALUES (?, ?, ?, ?)',(idno, name, course, level))
    conn.commit()
    conn.close()

    return 'Student added successfully'

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([username, password]):
        return "All fields are required", 400

    conn = get_db_connection()
    conn.execute('INSERT INTO users (userName, userPassword) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()
    return 'Registered Successfully'


@app.route('/editstudent', methods=['POST'])
def edit_student():
    idno = request.form['idno']
    name = request.form['name']
    course = request.form['course']
    level = request.form['level']

    conn = get_db_connection()
    conn.execute('''
        UPDATE students
        SET name = ?, course = ?, level = ?
        WHERE idno = ?
    ''', (name, course, level, idno))
    conn.commit()
    conn.close()

    return "Student updated successfully", 200
200
    
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
