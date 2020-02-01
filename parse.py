import json
import boto3
from PIL import Image, ImageDraw, ImageFont

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
    outname = document_name.split('.')[0]
    with open('{}.json'.format(outname), 'w') as outfile:
        json.dump(response, outfile)



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

def draw_answers(im, questions):
    coordinates = questions[0].main.box
    height = int(im.height*coordinates['Height'])

    text_layer = Image.new('RGBA', im.size, (255,255,255,0))
    fnt = ImageFont.truetype('arial.ttf', height)
    d = ImageDraw.Draw(text_layer)

    for question in questions:
        if len(question.children) == 0:
            coordinates = question.main.box
            d.text((im.width*coordinates['Left'], im.height*coordinates['Top']+(height*1.4)),"Answer", font=fnt, fill=(0,0,0,255))

    out = Image.alpha_composite(im, text_layer)

    out.show()
    

def print_response(response):
    print(json.dumps(response, indent=4, sort_keys=True))



if __name__ == '__main__':
    im = Image.open('grid.png')

    with open('grid.json') as json_file:
        response = json.load(json_file)

    # build list of questions from AWS Response
    questions = pull_questions_grid(response)

    # draw answers to corresponding questions
    draw_answers(im, questions)

    
   
        
