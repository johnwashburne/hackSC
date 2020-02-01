import json
import boto3
import os.path
from PIL import Image, ImageDraw, ImageFont

caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

class Controller:

    def __init__(self, file=None):
        if file != None:
            self.file = file
            self.textract()

    def change_file(self, file):
        self.file = file
        self.textract()

    def textract(self):
        outname = self.file.split('.')[0] + '.json'
        if not os.path.isfile(outname):
            with open(self.file, 'rb') as document:
                image_bytes = bytearray(document.read())

            textract = boto3.client('textract', region_name='us-east-1',
                                    aws_access_key_id='AKIAJOZSX5OBM2FX4G2Q',
                                    aws_secret_access_key='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')

            self.response = textract.detect_document_text(Document={'Bytes': image_bytes})

            
            with open('{}'.format(outname), 'w') as outfile:
                json.dump(self.response, outfile)
        else:
            with open(outname) as json_file:
                self.response = json.load(json_file)

    def get_questions(self):
        entries = []
        for block in self.response['Blocks']:
            
            if block['BlockType'] == "LINE" and block['Text'] != 'C' and block['Text'] != ')' and block['Text'] != 'b.' and block['Text'] != 'c.':
                box = block['Geometry']['BoundingBox']
                entries.append({'text': block['Text'], 'box':box})
                               
        questions = []
        children = []
        main = entries[0]

        for line in entries[1:]:
            if line['text'][0].isdigit():
                if 'Gender' in main['text'] or 'Marital' in main['text'] or 'you fluent in' in main['text']:
                    qtype = 'radio'
                elif 'Check' in main['text']:
                    qtype = 'checkbox'
                else:
                    qtype = 'text'

                questions.append({'main':main, 'children':children, 'qtype':qtype})
                children = []
                main = line
            else:
                children.append(line)

        if 'Gender' in main['text'] or 'Marital' in main['text']:
            qtype = 'radio'
        elif 'Check' in main['text']:
            qtype = 'checkbox'
        else:
            qtype = 'text'
        questions.append({'main':main, 'children':children, 'qtype':qtype})

        self.questions = questions
        print(len(questions))
        return questions

if __name__ == "__main__":
    c = Controller("grid-bottom.png")
    questions = c.get_questions()
    for q in questions:
        print(q['main']['text'])
        for c in q['children']:
            print('\t' + c['text'])
    with open("i589-bottom.json", "w") as outfile:
        json.dump(questions, outfile)
