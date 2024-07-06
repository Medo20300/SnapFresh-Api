import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'medhat2030'
app.config['MYSQL_DB'] = 'UserAuthentication'
app.config['MYSQL_UNIX_SOCKET'] = '/var/run/mysqld/mysqld.sock'
mysql = MySQL(app)

# Secret key for session management
app.secret_key = 'your_secret_key'

# User roles
USER = 0
ADMIN = 1

# Check if user is logged in (session)
def is_logged_in():
    return 'loggedin' in session

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Check if 'role' is in account and handle accordingly
            session['role'] = account.get('role', USER)
            flash('Logged in successfully!', 'success')  # Flash message on successful login
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        else:
            # Insert into accounts with 'role' included
            cursor.execute('INSERT INTO accounts (username, password, email, role) VALUES (%s, %s, %s, %s)', (username, password, email, USER,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

# User logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')  # Flash message on logout
    return redirect(url_for('index'))

# Home page
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

# Predict page (dummy route, adjust as per your application)
@app.route('/predict', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('predict', filename=filename))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
