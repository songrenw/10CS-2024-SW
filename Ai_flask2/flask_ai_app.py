from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from openai import OpenAI, RateLimitError
import openai
from config import Config #import Config def from cofig.py
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
app.secret_key = "A3f9K7pQ2" #app secret key
# Recaptcha key
RECAPTCHA_SECRET_KEY = Config.RECAPTCHA_SECRET_KEY#get recaptcha secret key from config,py which link to the .env files
RECAPTCHA_SITE_KEY = "6LflYjwqAAAAAEsmC748UKQYO5F_yNL8lN3rzNUB"

genai.configure(api_key=Config.GOOGLE_API_KEY) #gemini api from .env file through Config def
model=genai.GenerativeModel('gemini-1.5-flash') #identify what model is gemini using, in this case is 'genmini 1.5 flash"
client = OpenAI(api_key=Config.OPENAI_API_KEY) # get open ai api from .env files throgh config def
#cached_llm = Ollama(model="llama3.1")
api_endpoint= 'http://localhost:11434/api/chat' # defind the api endpoint that is going to be used(ollama)

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
            user INTEGER NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            model TEXT NOT NULL,
            FOREIGN KEY (user) REFERENCES users(id)
        )
    ''') # create history table and user table if it not exists
    conn.commit()  # commits the change to the database
    conn.close()  # closes the connection to the database to free up resources/memory

@app.route('/') # app route '/' is the default flask app route, which means that the website will directed to this app route when stated
def home():
    return render_template('home.html') # default route return to 'home.html', this is the default html page as it allow the user to either login or register an account and use the ai chatbot.
@app.route('/login')
def login():
    # Handle login logic
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login_post():
    username = request.form['username'] # get the username from the database
    password = request.form['password']  # gets the password from the form
    conn = sqlite3.connect('ai_flask.db') # connet to the database
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    # ? is a placeholder for the values that will be passed in the execute() function
    # (username) are the value that will be passed in the execute() function
    # This is a parameterised query to prevent SQL injection attacks
    user = cursor.fetchone()  # fetches the result
    conn.close() # close the database
    if user and check_password_hash(user[2], password):  # Check user and hashed password and the plain password is correct.
        session['user'] = user[1] # session the user
        return redirect(url_for('welcome')) #return to welcome page
    else:
        flash('Username or Password Incorrect') # flash the error message
        return redirect(url_for('login')) # reload the login page to allow user to login again.

@app.route('/register', methods=['GET', 'POST'])
def register():
    # when request method is post, send data such as user register to the db, and return to the html when the method is get, so there wont be 'method no allow error'
    if request.method == 'POST':
        # Validate reCAPTCHA
        recaptcha_response = request.form['g-recaptcha-response'] #get the recaptcha response from the form.
        if not recaptcha_response: # if the user did not click the 'im not a robot' tick bok
            flash('Please complete the reCAPTCHA.', 'error') #return a message
            return redirect(url_for('register')) #reload the register url

        # Verify reCAPTCHA with Google, using the url
        recaptcha_verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }

        recaptcha_verify = requests.post(recaptcha_verification_url, data=data)
        # send a post requets to the url with the data
        recaptcha_result = recaptcha_verify.json() #tranform the verification response from jason to python

        if not recaptcha_result.get('success'): #if the varification fails
            flash('Please try again.', 'error') #flash the error
            return redirect(url_for('register'))

        # Handle registration logic if reCAPTCHA is valid
        #when method is post, try the below.
        try:
            username = request.form['username'] #defind username and password vairable from the form.
            password = request.form['password']
            token = request.form['g-recaptcha-response']
            #hashed the password
            hashed_password = generate_password_hash(password, method='scrypt', salt_length=8) #generate hashed password using scrypt methond.

            conn = sqlite3.connect('ai_flask.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))
        # this is here to prevent as a syntax choice, as if there is keyerror, it will return back to register.
        except KeyError as e:
            flash('An error occurred during registration.', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/welcome')
def welcome():
    if 'user' not in session: # a syntax choice. return to login, so it wont run it to error while log in to welcome.html as the welcome.html can not found the user in session, as the user didn't login.
        return redirect(url_for('login'))
    if 'user' in session: # if user in session
        user = session['user'] #defind user variable as session user
        return render_template('welcome.html', user=user) # return user variable to welcome html
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
    user_message = request.form['message'] # get the user input from the form.
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
                 return render_template('chatgpt.html', error="Error: Rate limit exceeded. Please try again later.")# return error message if exceed the rate limit.

    # If GET request, simply render the form
    return render_template('chatgpt.html')

@app.route('/llama', methods=["GET", "POST"])
def llama_post():
    # if the user didn't login, they are redirect to login
    if 'user' not in session:
        return redirect(url_for('login'))

    messages = [] # empty list that will update every time the user enter a message and every time Ai sends a reponse
    if request.method == 'POST': # if the method is post do the following command. This is required to make sure the form(user input) is summited using the POST method, which the POST method is used to send data to the server, while GET is used to retreve data and display it on the website.
        query = request.form['query'] # Get the user input from the query form at llama.html, in a form of input textbox and a submit button, which can be found in llama.html.

        # Append user's message/updating messages list to send to the AI model
        messages.append({'role': 'user', 'content': query})
        model = 'llama 3.1'
        # Prepare data for the API request, which the data is collected from the list of message so AI can response to the query the user have inputed.
        data = {
            'model': 'llama3.1',
            'stream': False,
            'messages': messages
        }

        # Make the API request, which send API the data that is been collected through request.post and the api_endpoint is the place where the AI will response and the response is being sent using Json format, using jason as it is popular and flexable formate for data exchange(https://www.oracle.com/au/database/what-is-json/).
        response = requests.post(api_endpoint, json=data)

        if response.status_code == 200: #This is implemented to check if the api call is successful, which http 200 meaning that it is a successful response(https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200).
            response_data = response.json() # This is to convert API response in Json to Python
            assistant_response = response_data['message']['content'] # this recieve 'content' data from messages list, which is the ai responses.

            # Append the assistant's response to the message list. Add assistant_response to the message list
            messages.append(response_data['message'])
            # connect the database and store the query and responses in it to store and collect user AI history so they can see it.
            # connect to the database using sqlite
            conn = sqlite3.connect('ai_flask.db')
            cursor = conn.cursor() # creates a cursor object to interact with the database using SQL commands
    # cursor.execute() is used to execute SQL commands
            # insert user history into the database. This create a new row in the history tabs, to recoard user AI history
            cursor.execute('INSERT INTO history (user, query, response, model) VALUES (?, ?, ?, ?)',
                           (session['user'], query, assistant_response, model))
            # ? is a placeholder for the values that will be passed in the execute() function,
            # ? is the placeholder used to prevent ssl attack.
            conn.commit() #commit is used to save the change
            conn.close() # this close the database to free up resources

            # Render the result, state query and response variable and return it to the html. So llama.html can display the responses on the website
            return render_template('llama.html', query=query, assistant_response=assistant_response)
        else:
            # else if didn't get response, return the error and display on the html
            return render_template('llama.html', error='Failed to get response from Llama2.')
    # return to llama.html if method is GET, This allow the .html to be display on the website to let user ineract.
    return render_template('llama.html')

@app.route("/llama2", methods=["GET", "POST"]) #same as the /llama app route
def llama2_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    messages = []
    if request.method == 'POST':
        # Get the user input from the form
        query = request.form['user_input']

        model = 'llama 2'
        # Append user's message
        messages.append({'role': 'user', 'content': query})

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

            # connect to the database
            conn = sqlite3.connect('ai_flask.db')
            cursor = conn.cursor()
            # insert user history into the database
            cursor.execute('INSERT INTO history (user, query, response, model) VALUES (?, ?, ?, ?)',
                           (session['user'], query, assistant_response, model))
            conn.commit()
            conn.close()

            # Render the result on the web page
            return render_template('llama2.html', user_input=query, assistant_response=assistant_response)
        else:
            return render_template('llama2.html', error='Failed to get response from Llama2.')

    return render_template('llama2.html')

@app.route('/gemini', methods=['GET', 'POST'])
def gemini(): # if user not in session redirect to login, so the user must login before using any AI model.
    if 'user' not in session:
        return redirect(url_for('login'))

    model_use = 'Gemini 1.5 flash' #identify the model, so the user can know what model they using to get the response when viewing the history.
    if request.method == 'POST':

        query = request.form['input'] #request input from the html.

        output = model.generate_content(query).text # generate the output based the the query, which gemini generate process the query using generate_content() method and return with an result that is store in the output variable. The model is using the model identify at the top.
        # connect to the database
        conn = sqlite3.connect('ai_flask.db')
        cursor = conn.cursor()
        # insert user history into the database
        cursor.execute('INSERT INTO history (user, query, response, model) VALUES (?, ?, ?, ?)',
                       (session['user'], query, output, model_use))
        conn.commit()
        conn.close()
        return render_template('gemini.html', input=query, output=output)

    return render_template('gemini.html')

@app.route('/history')
def history():
    # if user not login, return to login
    if 'user' not in session:
        return redirect(url_for('login'))

    current_user = session['user'] # get the current user data,
    # Connect to the database
    conn = sqlite3.connect('ai_flask.db')
    cursor = conn.cursor()  # creates a cursor object to interact with the database using SQL commands
    # cursor.execute() is used to execute SQL commands
    # Fetch all records from the history table that the current user that is login have.
    cursor.execute('SELECT query, response, model FROM history WHERE user = ?', (current_user,)) #seclect the history that belong to the user that is in session(who is login to the app). So the history page doesnt display history other than the user that is login.
    # ? is a placeholder for the values that will be passed in the execute() function,
    chat_history = cursor.fetchall() # fetch the result
    conn.close() #close database



    # Pass the records to the template and display it in history html
    return render_template('history.html', history=chat_history)


if __name__ == '__main__':
    init_db() # calls the init_db() function to initialise
    app.run(port=5000, debug=True) # this start the flask app, where the server run at port 5000.
