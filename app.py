from flask import Flask, render_template, request, redirect, jsonify
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
import numpy as np
from dotenv import load_dotenv
import os
from flask_cors import CORS  

load_dotenv()
HuggingFaceApiKey = os.getenv("HuggingFaceApiKey")


app = Flask(__name__)
CORS(app, origins='chrome-extension://ooiefbeaelfhmbchpihnfblpkcaclkkf')  

# Initialize an empty list to store news URLs
news_urls_question = ["", ""]
news_summarization_url = ""

data = ""
data1 = ""

@app.route('/')
def index():
    return render_template('index.html', news_urls=news_urls_question)

@app.route('/question')
def question():
    return render_template('question.html', news_urls=news_urls_question)

@app.route('/summarization')
def summarization():
    return render_template('summarization.html', news_urls=news_urls_question)

@app.route('/add_urls', methods=['POST'])
def add_urls_question():
    global data
    if request.method == 'POST':
        # Get the updated URLs from the form
        updated_url1 = request.form['url1']
        updated_url2 = request.form['url2']
        # Update the news_urls list
        news_urls_question[0] = updated_url1
        news_urls_question[1] = updated_url2
        # Redirect back to the index page
        if(updated_url1 != "" or updated_url2 != ""):
            if(updated_url1 == ""):
                updated_url1 = updated_url2
            if(updated_url2 == ""):
                updated_url2 = updated_url1

            loader = UnstructuredURLLoader(urls=[
                updated_url1,
                updated_url2])
            data = loader.load()
            data = str(data)
            
            splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
            )

            data = splitter.split_text(data)

            
        return redirect('/question')
    # If it's a GET request, render the edit_urls.html template
    return render_template('edit.html', news_urls=news_urls_question)

@app.route('/submit_question', methods=['POST'])
def submit_question():
    global data
    if request.method == 'POST':
        question = request.form['question']
        context = ""
        answer = ""  # Initialize answer variable
        print(data)
        
        if(data != ""): 
            headers ={"Authorization": HuggingFaceApiKey}
            API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.json()
            
            data_ = query(
                {
                    "inputs": {
                    "source_sentence": question,
                    "sentences": data,
                    }
                }
            )

            data_array = np.array(data_)

            max_indices = data_array.argsort()[-2:][::-1]

            for i in max_indices:
                context = context + data[i]

            API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"

            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.json()
            data_ = query(
                {
                    "inputs": {
                        "question": question,
                        "context": context,
                    }
                }
            )

            answer = data_["answer"]  # Get the answer
            print("Retrieved answer:", answer)
        return render_template('question.html', news_urls=news_urls_question, answer=answer)  # Pass answer to template
'''
@app.route('/add_urls_summarization', methods=['POST'])
def add_urls_summarization():
    global data1
    if request.method == 'POST':
        news_summarization_url = request.form['url1']

        if(news_summarization_url != ""):
            loader = UnstructuredURLLoader(urls=[
                news_summarization_url])
            data1 = loader.load()
            data1 = str(data1)

            headers ={"Authorization": HuggingFaceApiKey}
            
            API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.json()
            data_ = query(
                {
                    "inputs": data1,
                    "parameters": {"do_sample": False},
                }
            )
            summary = data_[0]['summary_text']
            # Get the summary text

            return render_template('summarization.html', summary=summary)  # Render the summarization template with summary data

    # If it's a GET request or the URL is empty, render the edit_urls.html template
    return render_template('edit.html', news_urls=news_urls_question)
'''


@app.route('/add_urls_summarization', methods=['POST'])
def add_urls_summarization():
    global data1
    if request.method == 'POST':
        request_data = request.json  # Get JSON data from the request
        print(request_data)  # Print the JSON data for debugging purposes

        # Extract the URL from the JSON data
        news_summarization_url = request_data.get('url1', '')  # Use get() to avoid KeyError if 'url1' is missing

        if news_summarization_url:
            loader = UnstructuredURLLoader(urls=[news_summarization_url])
            data1 = loader.load()
            data1 = str(data1)

            headers = {"Authorization": HuggingFaceApiKey}
            
            API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.json()
            
            data_ = query(
                {
                    "inputs": data1,
                    "parameters": {"do_sample": False},
                }
            )

            summary = data_[0]['summary_text']
            # Get the summary text

            return jsonify({"summary": summary})  # Return JSON response with the summary

    # If it's a GET request or the URL is empty, return an error response
    return jsonify({"error": "No URL provided"}), 400



if __name__ == '__main__':
    app.run(debug=True)
