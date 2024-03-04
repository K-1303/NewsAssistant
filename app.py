from flask import Flask, render_template, request, jsonify
from langchain.document_loaders import UnstructuredURLLoader
import requests
#from flask_cors import CORS  
from flask import render_template_string


app = Flask(__name__)
#CORS(app, origins='ADD_EXTENSION_URL_HERE')  

# Initialize an empty list to store news URLs
news_summarization_url = ""

data1 = ""

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def add_urls_summarization():
    global data1
    if request.method == 'POST':
        news_summarization_url = request.form['url1']

        if(news_summarization_url != ""):
            loader = UnstructuredURLLoader(urls=[
                news_summarization_url])
            data1 = loader.load()
            data1 = str(data1)

            
            API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
            def query(payload):
                response = requests.post(API_URL, json=payload)
                return response.json()
            data_ = query(
                {
                    "inputs": data1,
                    "parameters": {"do_sample": False},
                }
            )
            summary = data_[0]['summary_text']
            # Get the summary text

            return render_template_string(open("templates/index.html").read(), summary=summary)  # Render the index.html template with summary data

    # If it's a GET request or the URL is empty, render the edit_urls.html template
    return render_template('index.html')


# For API requests
'''
@app.route('/summarize', methods=['POST'])
def summarize():
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
'''

if __name__ == '__main__':
    app.run(debug=True)
