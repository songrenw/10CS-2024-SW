from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
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
        password TEXT NOT NULL,
        age INTEGER NOT NULL
    )
    ''')
    conn.commit()  # commits the change to the database
    conn.close()  # closes the connection to the database to free up resources/memory

@app.route('/')
def home():
    return render_template('home.html')

# Main code to run the flask app nd initialise the database
if __name__ == '__main__':
    init_db() # calls the init_db() function to initialise
    app.run(port=5000, debug=True)