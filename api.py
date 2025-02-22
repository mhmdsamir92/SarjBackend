from flask import Flask, request, jsonify
import requests
import json
import os
from groq import Groq
from data import get_book_details, insert_book_details, get_all_history


app = Flask(__name__)

# Set your Groq AI API key and secret
GROQ_API_KEY = 'trial1'
GROQ_API_SECRET = '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'

# Set the Gutenberg project API endpoint
GUTENBERG_API_ENDPOINT = 'https://www.gutenberg.org'

# Set the Groq AI API endpoint
GROQ_API_ENDPOINT = 'https://api.groq.ai/v1/analyze'

SYSTEM_PROMPT = """
You are a summarization engine that outputs in markdown style. Users will feed you a piece of text, and you will return ONLY a summary of the content provided at a specified level of detail. Below are the allowed levels for your summaries:
- Summary Level 1: Headline Summary - Provide a 10-20 words with a 
single sentence bullet point headline that captures the overarching 
theme or main point for the content for each paragraph.

- Summary Level 2: Sentence-Level Summary - Provide a 20-30 words summary with 1-2 simple sentences that capture the main point in the text. 

- Summary Level 3: Paragraph Level-Summary - Provide a bullet points 
summary where each bullet points is a single sentence or headline 
(10-15 words) that captures the overarching theme or main point for 
each paragraph in the text.

- Summary Level 4: One-Paragraph Summary - Provide a 30-50 words summary 
where you introduce the main point, key arguments, or narrative arc 
in a short paragraph, adding context to the headline.

- Summary Level 5: Executive Summary - Provide a 50-80 words summary with 
the key points, findings, and implications in a high-level overview 
suitable for decision-making. 

- Summary Level 6: Structured Summary - Provide a 80-100 words summary 
where you break down the content into predefined relevant sections 
(one example would be: Introduction, Methods, Results, Conclusion if its a paper), 
providing a clear overview of each major component.

- Summary Level 7: Detailed Summary - Summarize in 100-120 words 
covering all main points and supporting arguments or evidence in a 
comprehensive summary that conveys a thorough understanding. 

Inputs from the user will always follow this structure:

'''
text input:
<user text input>
Summary level: <the summary level as a number from 1-10>
output:
'''"""

@app.route('/get-past-searches', methods=['GET'])
def get_past_searches():
    books = get_all_history()
    return jsonify(books)

@app.route('/analyze', methods=['POST'])
def analyze_story():
    # Get the book ID from the request body
    book_id = request.get_json()['book_id']
    book = get_book_details(book_id)
    if book:
        return book

    # Fetch the text from the Gutenberg project
    text = fetch_text_from_gutenberg(book_id)

    title = fetch_book_title(book_id)
    import pdb; pdb.set_trace()
    is_book_inserted = insert_book_details({
        'book_id': book_id,
        'title': title,
        'author': title,
        'language': title,
        'summary': title,
        'sentiment': title,
        'key_characters': title,
        'book_text': text
    })

    # Analyze the story using Groq AI
    # analysis = analyze_text_with_groq(text)

    # Return the analysis as JSON
    # return jsonify({'analysis': analysis})
    return jsonify({
        'id': book_id,
        'title': title,
        'summary': title,
        'text': text,
        'is_book_inserted': is_book_inserted
    })

def fetch_text_from_gutenberg(book_id):
    # Construct the URL for the Gutenberg project API
    url = f'{GUTENBERG_API_ENDPOINT}/files/{book_id}/{book_id}-0.txt'

    # Send a GET request to the Gutenberg project API
    response = requests.get(url)

    # Return the text from the response
    return response.text

def fetch_book_title(book_id):
    url = f'{GUTENBERG_API_ENDPOINT}/ebooks/{book_id}'

    response = requests.get(url).text

    # Return the text from the response
    return response[response.find("<title>")+7:response.find("</title>")]


def analyze_text_with_groq(text):
    # Construct the headers for the Groq AI API
    import pdb; pdb.set_trace()
    client = Groq(
        api_key="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"
    )
    chat_completion = client.chat.completions.create(
    messages=[
        {   
            "role": "system",
            "content": SYSTEM_PROMPT
         },
        {
            "role": "user",
            "content": f"""
            text input:
            {text}
            Summary level: 7
            output:
            """
        }
    ],
    model="mixtral-8x7b-32768",
)
    return chat_completion.choices[0].message.content

    # headers = {
    #     'Authorization': f'Bearer {GROQ_API_KEY}',
    #     'Content-Type': 'application/json'
    # }

    # # Construct the payload for the Groq AI API
    # payload = {
    #     'text': text,
    #     'model': 'story',
    #     'output': 'json',
    #     'tasks': [
    #         {'task': 'key_characters'},
    #         {'task': 'language'},
    #         {'task': 'sentiment'},
    #         {'task': 'plot_summary'}
    #     ]
    # }

    # # Send a POST request to the Groq AI API
    # response = requests.post(GROQ_API_ENDPOINT, headers=headers, json=payload)

    # # Return the analysis from the response
    # return response.json()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")