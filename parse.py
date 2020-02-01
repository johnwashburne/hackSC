import json
import boto3

caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

class Question:

    def __init__(self, main, children):
        self.main  = main
        self.children = children

    def display(self):
        print(self.main)
        for i in self.children:
            print('\t{}'.format(i))

class Entry:
    def __init__(self, text, box):
        self.text = text
        self.box = box

    def __str__(self):
        return self.text

def textract(document_name):
    with open(document_name, 'rb') as document:
        image_bytes = bytearray(document.read())

    textract = boto3.client('textract', region_name='us-east-1',
                            aws_access_key_id='AKIAJOZSX5OBM2FX4G2Q',
                            aws_secret_access_key='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')

    response = textract.detect_document_text(Document={'Bytes': image_bytes})
    with open('form3.json', 'w') as outfile:
        json.dump(response, outfile)

def pull_text(response):
    all_text = []
    for block in response['Blocks']:
        if block['BlockType'] == "LINE" and block['Text'] != 'C' and block['Text'] != ')' and block['Text'] != 'b.' and block['Text'] != 'c.':
            all_text.append(block['Text'])
    return all_text

def pull_questions_grid(response):
    entries = []
    for block in response['Blocks']:
        
        if block['BlockType'] == "LINE" and block['Text'] != 'C' and block['Text'] != ')' and block['Text'] != 'b.' and block['Text'] != 'c.':
            box = block['Geometry']['BoundingBox']
            entries.append(Entry(block['Text'], box))
                           
    questions = []
    children = []
    main = entries[0]
    
    for line in entries[1:]:
        if line.text[0].isdigit():
            questions.append(Question(main, children))
            children = []
            main = line
        else:
            children.append(line)

    questions.append(Question(main, children))

    return questions
    

def print_response(response):
    print(json.dumps(response, indent=4, sort_keys=True))



if __name__ == '__main__':
    with open('response.json') as json_file:
        response = json.load(json_file)

    for i in pull_questions_grid(response):
        i.display()
        
