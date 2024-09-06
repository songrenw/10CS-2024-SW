from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
# Flask, the web app framework used to build the web application
# sqlite3 - used for interacting with SQLite3 database
# render_template, used to render the html template
# request, handles http requestes form the browswer
# redirect, url for, used for URL redirection to direct th user to the webpage
# session, manages the user info
# flash - used to display message to the user
# datatime - handle data and time poeration

app = Flask(__name__) # this creates an instance of the Flask class
app.secret_key = "A3f9K7pQ2"

def init_db():  # a function to initialise the database and create the users table if it doesn't exist
    conn = sqlite3.connect('ai_flask.db')  # connects to the database name basic_flask.db
    cursor = conn.cursor()  # creats a cursor object to interact with the database using SQL commands
    # cursor.execute() is used to execute SQL commands
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()  # commits the change to the database
    conn.close()  # closes the connection to the database to free up resources/memory

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login')
def login():
    # Handle login logic
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    username = request.form['username'] # get the username from the database
    password = request.form['password']  # gets the password from the form
    conn = sqlite3.connect('ai_flask.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    # ? is a placeholder for the values that will be passed in the execute() function
    # (username, passowrd) are the value that will be passed in the execute(0 function
    # This is a parameterised query to prevent SQL injection attacks
    user = cursor.fetchone()  # fetches the first row of the result
    conn.close()
    if user and check_password_hash(user[2], password):  # Check hashed password and the plain password user store in
        session['user'] = user[1]
        return redirect(url_for('welcome'))
    else:
        flash('Username or Password Incorrect') # flash the error message
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle registration logic
    if request.method == 'POST':
        try:
            username = request.form['username']  # gets the username from the form
            password = request.form['password']  # gets the password from the form
            # Hash the password before saving it
            hashed_password = generate_password_hash(password, method='scrypt', salt_length=8)
            conn = sqlite3.connect('ai_flask.db')  # connects to the database
            cursor = conn.cursor() # creates a cursor object to interact with the database
            # inserts the user details into the users table
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit() # commit the changes to the database
            conn.close()  # closes the connection to the database
            flash('User registered successfully!', 'success')  # displays a success message to the user
            return redirect(url_for('login'))  # redirects the user to the login page
        except KeyError as e:
            return render_template('register.html')
    return render_template('register.html')

@app.route('/welcome')
def welcome():
    if 'user' in session:
        user = session['user']
        return render_template('welcome.html', user=user)
    return redirect(url_for('login'))

@app.route('/logout/', methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))
# Main code to run the flask app nd initialise the database



if __name__ == '__main__':
    init_db() # calls the init_db() function to initialise
    app.run(port=5000, debug=True)