from flask import Flask, request, jsonify
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import time
import os
import pandas as pd
from flask_cors import CORS

# Constants
#CHATGPT_MODEL = "gpt-4-0613"
CHATGPT_MODEL = "gpt-3.5-turbo-16k"
CHATGPT_URL =  "https://api.openai.com/v1/chat/completions"

app = Flask(__name__)
CORS(app)


# Load the dataframe
current_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(current_dir,'RIS_library','embedded_abstracts.txt'),dtype=object)
df['ada_embedding'] = df['ada_embedding'].apply(lambda x: eval(x))  # convert string to list


@app.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
    global df
    data = request.get_json()
    response = openai.Embedding.create(
        input= data['text'],
        model="text-embedding-ada-002")
    
    embedding = response['data'][0]['embedding']
    #embedding = get_embedding(data['text'], model='text-embedding-ada-002')
    df['similarities'] = df.ada_embedding.apply(lambda x: cosine_similarity(x, embedding))
    res = df.sort_values('similarities', ascending=False).head(50)
    res = res[['title', 'secondary_title', 'year','abstract', 'accession_number', 'similarities']]
    
   
     # 'title', 'secondary_title', 'year', 'abstract', 'accession_number'のNaNを"NA"に置換
    res[['title', 'secondary_title', 'year','abstract', 'accession_number']] = res[['title', 'secondary_title', 'year','abstract', 'accession_number']].fillna("NA")
    # 'title', 'secondary_title', 'year', 'abstract', 'accession_number'の空文字列を"NA"に置換
    res[['title', 'secondary_title', 'year','abstract', 'accession_number']] = res[['title', 'secondary_title', 'year','abstract', 'accession_number']].replace("", "NA")
    print(res)
    return jsonify(res.to_dict('records'))




@app.route('/process_text', methods=['POST'])
def process_text():
    global CHATGPT_MODEL 

    data = request.get_json()
    text = data['text']
    model = data['model']

    print(f"""before: {text}""")

    if model == 'GPT3':
        CHATGPT_MODEL = "gpt-3.5-turbo-16k"
    elif model == 'GPT4':
        CHATGPT_MODEL = "gpt-4-0613"
    else:
        return jsonify({'error': 'Invalid model name'}), 400

    translated_text = translate_with_chatgpt(text)

    return jsonify({'result': translated_text})


def translate_with_chatgpt(text):
    prompt = f"""You are a skilled editor for a prestigious scientific journal. Your task is to rephrase the 
    following text, which is a part of a manuscript regarding hematopoietic stem cells, to make it suitable for academic publication. 
    If the text is written in Japanese, translate it into English suitable for academic publication. Please leave the brackets or braces 
    unchanged, and please provide only the revised text.\n\nOriginal Text:\n{text}\n\nRevised/Translated Text:"""
    data = create_chat_completion_with_retry(prompt, retries=3, delay=5)        
    translated_text = data["choices"][0]["message"]["content"].strip() # type: ignore
    
    print(f"""{translated_text}""")
    return translated_text


def create_chat_completion_with_retry(prompt, retries=3, delay=5):
    global CHATGPT_MODEL
    for _ in range(retries):
        try:
            data = openai.ChatCompletion.create(
                model= CHATGPT_MODEL,
                messages= [{"role": "user", "content": prompt}]
            )
            return data
        except Exception as e:  
            print(f"Request failed with {e}, retrying...")
            time.sleep(delay)  # Wait for 'delay' seconds before next retry

    # If control reaches here, all retries have failed
    return  {
        "choices": [{"message": {"content" : "Error was not resolved!"}}]
    }

if __name__ == '__main__':
    app.run(port=5000)