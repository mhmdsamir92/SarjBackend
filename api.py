from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import json
import os
from groq import Groq
from data import get_book_details, insert_book_details, get_all_history
from langchain.text_splitter import CharacterTextSplitter
from SummaryRecipe import SummaryRecipe


app = Flask(__name__)
cors = CORS(app)

MINIMUM_BOOK_TOKENS = 1000

# Set the Gutenberg project API endpoint
GUTENBERG_API_ENDPOINT = 'https://www.gutenberg.org'

@app.route('/get-past-searches', methods=['GET'])
@cross_origin()
def get_past_searches():
    books = get_all_history()
    return jsonify(books)

@app.route('/analyze', methods=['POST'])
@cross_origin()
def analyze_story():
    book_id = request.get_json()['book_id']
    book = get_book_details(book_id)
    if book:
        return book

    title = fetch_book_title(book_id)

    text = fetch_text_from_gutenberg(book_id)

    source = ''

    if len(text) < MINIMUM_BOOK_TOKENS:
        # This means that the text is not there
        source = 'title'
        analysis = analyze_title_with_groq(title, f'{GUTENBERG_API_ENDPOINT}/ebooks/{book_id}')
    else:
        # Analyze the story text
        source = 'text'
        analysis = analyze_text_with_groq(text)

    
    author = analysis['author']
    language = analysis['language']
    summary = analysis['summary']
    sentiment =  analysis['sentiment']
    key_characters =  ",".join(analysis['key_characters'])

    is_book_inserted = insert_book_details({
        'book_id': book_id,
        'title': title,
        'author': author,
        'language': language,
        'summary': summary,
        'sentiment': sentiment,
        'key_characters': key_characters,
        'book_text': text
    })

    return jsonify({
        'book_id': book_id,
        'title': title,
        'author': author,
        'language': language,
        'summary': summary,
        'sentiment': sentiment,
        'key_characters': key_characters,
        'source': source,
        'is_book_inserted': is_book_inserted
    })

def fetch_text_from_gutenberg(book_id):
    url = f'{GUTENBERG_API_ENDPOINT}/files/{book_id}/{book_id}-0.txt'

    response = requests.get(url)

    return response.text

def fetch_book_title(book_id):
    url = f'{GUTENBERG_API_ENDPOINT}/ebooks/{book_id}'

    response = requests.get(url).text

    title = response[response.find("<title>")+7:response.find("</title>")]

    title = title[:title.find("|")] 
    return title


def chunk_text(text):
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=20000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks


def analyze_title_with_groq(title, url):
    client = Groq(
        api_key=os.environ['GROQ_API_KEY']
    )
    prompt = """
        You are an expert summarizer tasked with creating a final summary given book title and book url.
        Combine the key points from the provided summaries into a cohesive and comprehensive summary.
        The final summary should be concise formatted in JSON using the schema: {json_format} and include the following information: \n 1. Author\n 2. Language of the text\n 3. Overall Sentiment\n 4. Summary 5. Key Characters \n\n
        book title: {title} \n
        book url: {url}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {   
                "role": "user",
                "content": prompt.format(
                    json_format=json.dumps(SummaryRecipe.model_json_schema(), indent=2),
                    title=title,
                    url=url)
            }
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"}
    )
    final_details = json.loads(chat_completion.choices[0].message.content)

    return final_details


def analyze_text_with_groq(text):
    # Construct the headers for the Groq AI API
    client = Groq(
        api_key=os.environ['GROQ_API_KEY']
    )
    prompt_per_chunk = """You are a highly skilled AI model tasked with summarizing text.
                    Please provide a 100-120 words summary for the following chunk of text in a concise manner,
                    Also identify the key characters and mention the language of the text. Do not omit any key details:\n\n{document}"""
    
    prompt_for_all_summaries = """
        You are an expert summarizer tasked with creating a final summary from summarized chunks.
        Combine the key points from the provided summaries into a cohesive and comprehensive summary.
        The final summary should be concise formatted in JSON using the schema: {json_format} and include the following information: \n 1. Author\n 2. Language of the text\n 3. Overall Sentiment\n 4. Summary 5. Key Characters \n\n{document}
    """

    summaries = []
    chunks = chunk_text(text)
    for chunk in chunks[:10]:
        chat_completion = client.chat.completions.create(
            messages=[
                {   
                    "role": "user",
                    "content": prompt_per_chunk.format(document=chunk)
                }
            ],
            model="llama3-8b-8192",
        )
        summaries.append(chat_completion.choices[0].message.content)
        print("Done chunk")
    

    all_summaries = "\n".join(summaries)

    chat_completion = client.chat.completions.create(
        messages=[
            {   
                "role": "user",
                "content": prompt_for_all_summaries.format(
                    json_format=json.dumps(SummaryRecipe.model_json_schema(), indent=2),
                    document=all_summaries)
            }
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"}
    )
    final_details = json.loads(chat_completion.choices[0].message.content)

    return final_details

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)