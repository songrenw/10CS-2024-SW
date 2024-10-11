from flask import Flask, request
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader

app = Flask(__name__)
folder_path = "db"
cached_llm = Ollama(model="llama3.1")

embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)

#print(response)

@app.route('/llama', methods=["POST"])
def llama_post():

    print("Post /llama called")
    json_content= request.json
    query = json_content.get["query"]

    print(f"query: {query}")
    response = cached_llm.invoke(query)

    print(response)

    response_answer = {"answer": response}
    return response_answer

"""
@app.route('/pdf', methods=["POST"])
def pdf_post():
    file = request.files["file"]
    file_name = file.filename
    save_file = "pdf/" + file_name #save to path
    file.save(save_file)
    print(f"filename: {file_name}")

    loader = PDFPlumberLoader(save_file)
    docs = loader.load_and_split()
    print(f"doc len={len(docs)}")

    chunks= text_splitter.split_documents(docs)
    print(f"chunks len={len(chunks)}")

    vector_store = Chroma.from_documents(documents=chunks, embedding=embedding, persist_directory=folder_path)

    vector_store.persist()

    response = {"status": "Successfully Uploaded", "filename": file_name, "doc_len": len(docs), "chunks" : len(chunks),}
    return response
    """
def start_app():
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__== "__main__":
    start_app()

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