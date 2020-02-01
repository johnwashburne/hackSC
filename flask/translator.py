from google.cloud import translate_v2 as translate
import os

credential_path = r"C:\Users\johnw\Documents\Github\hackSC\flask\Learn-74e2e02b54cc.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def translate_data(data, target):
    translate_client = translate.Client(target_language=target)
    for d in data:
        for key in d:
            if isinstance(d[key], list):
                for i in range(len(d[key])):
                    d[key][i] = translate_client.translate(d[key][i])[['translatedText']]
            else:
                d[key] = translate_client.translate(d[key])['translatedText']

    return data

def translate_questions(questions, target):
    translate_client = translate.Client(target_language=target)
    
    for q in questions:
        q['main']['text'] = translate_client.translate(q['main']['text'])['translatedText']
        for s in q['children']:
            s['text'] = translate_client.translate(s['text'])['translatedText']
    
    return questions
                    
                
