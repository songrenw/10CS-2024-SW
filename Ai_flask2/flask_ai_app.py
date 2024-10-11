from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from openai import OpenAI, RateLimitError
import openai
from config import Config
import time
import google.generativeai as genai

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
# Recaptcha key
RECAPTCHA_SECRET_KEY = Config.RECAPTCHA_SECRET_KEY

genai.configure(api_key=Config.GOOGLE_API_KEY)
model=genai.GenerativeModel('gemini-1.5-flash')
client = OpenAI(api_key=Config.OPENAI_API_KEY)
#cached_llm = Ollama(model="llama3.1")
api_endpoint= 'http://localhost:11434/api/chat'

def query_openai(api_key, prompt):
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {'prompt': prompt, 'max_tokens': 150}
    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
    return response.json()

def init_db():  # a function to initialise the database and create the users table if it doesn't exist
    conn = sqlite3.connect('ai_flask.db')  # connects to the da tabase name basic_flask.db
    cursor = conn.cursor()  # creats a cursor object to interact with the database using SQL commands
    # cursor.execute() is used to execute SQL commands
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''') # create history table if it not exists
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
    conn = sqlite3.connect('ai_flask.db') # connet to the data base
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
    if request.method == 'POST':
        # Validate reCAPTCHA
        recaptcha_response = request.form['g-recaptcha-response']
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA.', 'error')
            return redirect(url_for('register'))

        # Verify reCAPTCHA with Google
        recaptcha_verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
            'remoteip': request.remote_addr
        }
        #bypass verify, due to SLL error
        recaptcha_verify = requests.post(recaptcha_verification_url, data=data, verify=False)
        recaptcha_result = recaptcha_verify.json()

        if not recaptcha_result.get('success'):
            flash('Please try again.', 'error')
            return redirect(url_for('register'))

        # Handle registration logic if reCAPTCHA is valid
        try:
            username = request.form['username']
            password = request.form['password']
            #hashed the password
            hashed_password = generate_password_hash(password, method='scrypt', salt_length=8)
            conn = sqlite3.connect('ai_flask.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))
        except KeyError as e:
            flash('An error occurred during registration.', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/welcome')
def welcome():
    if 'user' in session:
        user = session['user']
        return render_template('welcome.html', user=user)

@app.route('/select_model', methods=['POST'])
def select_model():
    selected_model = request.form.get('route')  # Get the selected route from the form
    if selected_model:
        return redirect(selected_model)  # Redirect to the selected route
    return redirect(url_for('welcome'))  # If no selection, return to welcome page

    return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None) # remove user from session
    print('pop')
    return redirect(url_for('home')) # redirect to home route when logout
# Main code to run the flask app nd initialise the database

@app.route('/chatgpt')
def chat_page():
    return render_template('chatgpt.html')

@app.route("/chatgpt",methods=["GET", "POST"])
def chatgpt():
    user_message = request.form['message']
    print(user_message)
    print(client)

    retries = 3
    for i in range(retries):
        try:
            # Call OpenAI API
            response = client.chat.completions.create(model="gpt-4o-mini",  # Use the cheaper model if possible
                                                      messages=[
                                                          {"role": "user", "content": user_message}
                                                      ],
                                                      max_tokens=150,
                                                      temperature=0.7)

            chatbot_reply = response.choices[0].message.content.strip()
            return {'message': chatbot_reply}

        except RateLimitError:  # Catch the rate limit error properly
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff: wait and retry
            else:
                return {'message': "Error: Rate limit exceeded. Please try again later."}

    # If GET request, simply render the form
    return render_template('chatgpt.html')

@app.route('/llama', methods=["GET", "POST"])
def llama_post():
    # if the user didn't login, they are redirect to login
    if 'user' not in session:
        return redirect(url_for('login'))
    #if method = to POST
    '''
    if request.method == 'POST':
        print("Post //llama called")
        query = request.form['query']
        data = {
            'model': 'llama3.1',
            'stream': False,
            'messages': query
        }

        print(f"YOU: {query}")
        response = cached_llm.invoke(query)
        #response = requests.post(api_endpoint, json=data)
        # connect to the database
        conn = sqlite3.connect('ai_flask.db')
        cursor = conn.cursor()
        # insert user history into the database
        cursor.execute('INSERT INTO history (user, query, response) VALUES (?, ?, ?)', (session['user'], query, response))
        conn.commit()
        conn.close()
        print(response)
        return render_template("llama.html", response=response)

        #if response.status_code == 200:
            #response_data = response.json()

            #assistant_response = response_data
    #if GET request, just show the form
    return render_template("llama.html")
    '''
    messages = []
    if request.method == 'POST':
        # Get the user input from the form
        query = request.form['query']

        # Append user's message
        messages.append({'role': 'user', 'content': query})

        # Prepare data for the API request
        data = {
            'model': 'llama3.1',
            'stream': False,
            'messages': messages
        }

        # Make the API request
        response = requests.post(api_endpoint, json=data)

        if response.status_code == 200:
            response_data = response.json()
            assistant_response = response_data['message']['content']

            # Append the assistant's response to the message list
            messages.append(response_data['message'])

            # connect to the database
            conn = sqlite3.connect('ai_flask.db')
            cursor = conn.cursor()
            # insert user history into the database
            cursor.execute('INSERT INTO history (user, query, response) VALUES (?, ?, ?)',
                           (session['user'], query, assistant_response))
            conn.commit()
            conn.close()

            # Render the result
            return render_template('llama.html', query=query, assistant_response=assistant_response)
        else:
            return render_template('llama.html', error='Failed to get response from Llama2.')

    return render_template('llama.html')

@app.route("/llama2", methods=["GET", "POST"])
def llama2_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    messages = []
    if request.method == 'POST':
        # Get the user input from the form
        user_input = request.form['user_input']

        # Append user's message
        messages.append({'role': 'user', 'content': user_input})

        # Prepare data for the API request
        data = {
            'model': 'llama2',
            'stream': False,
            'messages': messages
        }

        # Make the API request
        response = requests.post(api_endpoint, json=data)

        if response.status_code == 200:
            response_data = response.json()
            assistant_response = response_data['message']['content']

            # Append the assistant's response to the message list
            messages.append(response_data['message'])

            # Render the result on the web page
            return render_template('llama2.html', user_input=user_input, assistant_response=assistant_response)
        else:
            return render_template('llama2.html', error='Failed to get response from Llama2.')

    return render_template('llama2.html')

@app.route('/gemini', methods=['GET', 'POSt'])
def gemini():
    if 'user' not in session:
        return redirect(url_for('login'))

    prompt = ""
    output = ""
    if request.method == 'POST':
        prompt = request.form['input']
        output = model.generate_content(prompt).text
    return render_template('gemini.html', input=input, output=output)


if __name__ == '__main__':
    init_db() # calls the init_db() function to initialise
    app.run(port=5000, debug=True)
