import json
import boto3
from PIL import Image, ImageDraw, ImageFont

caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

class Question:

    def __init__(self, main, children, qtype):
        self.main  = main
        self.children = children
        self.qtype = qtype

    def display(self):
        print(self.main)
        for i in self.children:
            print('\t{}'.format(i))
    def __str__(self):
        return str(self.main)

class Entry:
    def __init__(self, text, box):
        self.text = text
        self.box = box

    def __str__(self):
        return str(self.text)

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
            if 'Gender' in main.text or 'Marital' in main.text:
                qtype = 'radio'
            elif 'Check' in main.text:
                qtype = 'checkbox'
            else:
                qtype = 'textbox'

            print(main, qtype)
            questions.append(Question(main, children, qtype))
            children = []
            main = line
        else:
            children.append(line)

    if 'Gender' in main.text or 'Marital' in main.text:
        qtype = 'radio'
    elif 'Check' in main.text:
        qtype = 'checkbox'
    else:
        qtype = 'textbox'
    questions.append(Question(main, children, qtype))

    return questions

def draw_answers(im, questions):
    coordinates = questions[0].main.box
    height = int(im.height*coordinates['Height'])

    text_layer = Image.new('RGBA', im.size, (255,255,255,0))
    fnt = ImageFont.truetype('arial.ttf', height)
    d = ImageDraw.Draw(text_layer)

    for question in questions:
        if question.qtype == 'textbox' and len(question.children) == 0:
            coordinates = question.main.box
            d.text((im.width*coordinates['Left'], im.height*coordinates['Top']+(height*1.4)),"Answer", font=fnt, fill=(0,0,0,255))
        elif question.qtype == 'textbox':
            for subquestion in question.children:
                coordinates = subquestion.box
                d.text((im.width*coordinates['Left'], im.height*coordinates['Top']+(height*1.4)),"Answer", font=fnt, fill=(0,0,0,255))
        elif question.qtype == 'checkbox':
            coordinates = question.children[2].box
            d.text((im.width*coordinates['Left']-im.width*.026, im.height*coordinates['Top']),"X", font=fnt, fill=(0,0,0,255))
        else:
            coordinates = question.children[0].box
            d.text((im.width*coordinates['Left']-im.width*.03, im.height*coordinates['Top']),"X", font=fnt, fill=(0,0,0,255))

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

    
   
        
