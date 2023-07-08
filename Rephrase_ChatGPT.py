from flask import Flask, request, jsonify
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import time
import os
import pandas as pd
from flask_cors import CORS
import deepl
from Bio import Entrez



# Constants
#CHATGPT_MODEL = "gpt-4-0613"
CHATGPT_MODEL = "gpt-3.5-turbo"
CHATGPT_URL =  "https://api.openai.com/v1/chat/completions"

app = Flask(__name__)
CORS(app)


# Load the dataframe
current_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(current_dir,'RIS_library','embedded_abstracts.txt'),dtype=object)
df['ada_embedding'] = df['ada_embedding'].apply(lambda x: eval(x))  # convert string to list




@app.route('/search_literature', methods=['POST'])
def search_literature():
    data= request.get_json()
    text = data['text']
    mode =  data['mode']
    res = pd.DataFrame(['title', 'secondary_title', 'year','abstract', 'accession_number', 'similarities'])
    res = jsonify(res.to_dict('records'))
    
    if mode == 'Embedding':
        res = calculate_similarity(text)
    elif mode == 'Pubmed':
        res = search_pubmed(text)
    else:
        pass
    return res




def calculate_similarity(text):
    global df
   # data = request.get_json()
    response = openai.Embedding.create(
        input= text,
        model="text-embedding-ada-002")
    
    embedding = response['data'][0]['embedding'] # type: ignore
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

def search_pubmed(text):
    Entrez.email = os.getenv("EMAIL_ADDRESS")  # Always tell NCBI who you are
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax='50',
                            retmode='xml', 
                            term=text)
    results = Entrez.read(handle)
    ids = results['IdList'] # type: ignore
    handle = Entrez.efetch(db='pubmed', id=ids, retmode='xml')
    papers = Entrez.read(handle)['PubmedArticle'] # type: ignore
    res = []
    for paper in papers:
        try:
            title = paper['MedlineCitation']['Article']['ArticleTitle']
        except KeyError:
            title = 'NA'
        
        try:
            secondary_title = paper['MedlineCitation']['MedlineJournalInfo']['MedlineTA']
        except KeyError:
            secondary_title = 'NA'

        try:
            year = paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
        except KeyError:
            year = 'NA'

        try:
            abstract = paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        except KeyError:
            abstract = 'NA'
        
        try:
            accession_number = paper['MedlineCitation']['PMID']
        except KeyError:
            accession_number = 'NA'
        
        res.append({
            'title': title,
            'secondary_title': secondary_title,
            'year': year,
            'abstract': abstract,
            'accession_number': accession_number,
            'similarities': 0.0 # this is a placeholder, replace with real calculation if necessary
        })
    return jsonify(res)



@app.route('/process_text', methods=['POST'])
def process_text():
    global CHATGPT_MODEL 

    data = request.get_json()
    response_text = "If this sentence is shwon, something went wrong"
    text = data['text']
    model = data['model']
    mode =  data['mode']

    print(f"""before: {text}""")

    if model == 'GPT3':
        CHATGPT_MODEL = "gpt-3.5-turbo"
    elif model == 'GPT4':
        CHATGPT_MODEL = "gpt-4"
    elif model == 'DEEPL':
        pass
    else:
        return jsonify({'error': 'Invalid model name'}), 400

    if mode == 'rephrase':
        response_text = translate_with_chatgpt(text)
    elif mode == 'complete':
        response_text = complete_with_chatgpt(text)
    elif mode == 'translate':
        response_text = translate_with_deepl(text)

    print(response_text)

    return jsonify({'result': response_text})


def translate_with_chatgpt(text):
    prompt = f"""You are a skilled editor for a prestigious scientific journal. Your task is to rephrase the 
    following text, which is a part of a manuscript regarding hematopoietic stem cells, to make it suitable for academic publication. 
    If the text is written in Japanese, translate it into English suitable for academic publication. Please leave the brackets or braces 
    unchanged, and please provide only the revised text.\n\nOriginal Text:\n{text}\n\nRevised/Translated Text:"""
    data = create_chat_completion_with_retry(prompt, retries=3, delay=5)        
    translated_text = data["choices"][0]["message"]["content"].strip() # type: ignore
    
    print(f"""{translated_text}""")
    return translated_text

def complete_with_chatgpt(text):
    prompt = f"""You are a skilled editor for a prestigious scientific journal. 
    I am currently writing a paper in English about hematopoietic stem cells and I need your help in completing a paragraph. 
    Here's the context and the last sentence I wrote: {text}. \n\n Could you please generate 3 candidates of continuation based on this?"""
    data = create_chat_completion_with_retry(prompt, retries=3, delay=5)        
    translated_text = data["choices"][0]["message"]["content"].strip() # type: ignore
    translated_text = translated_text.split(':')[1].strip()
    print(f"""{translated_text}""")
    return translated_text



def translate_with_deepl(text):
    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
    #DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate'
    translator = deepl.Translator(DEEPL_API_KEY, verify_ssl=False) # type: ignore
    result = translator.translate_text(text, target_lang="EN-US").__str__()
    print(f"""{result}""")
    return result


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