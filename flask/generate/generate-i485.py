import json
import boto3
import os.path

caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

class Controller:

    def __init__(self, file=None):
        if file != None:
            self.file = file
            self.credentials = json.load(open('credentials.json', 'r'))
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
                                    aws_access_key_id=self.credentials['access_key'],
                                    aws_secret_access_key=self.credetials['secret_key'])

            self.response = textract.detect_document_text(Document={'Bytes': image_bytes})

            
            with open('{}'.format(outname), 'w') as outfile:
                json.dump(self.response, outfile)

        else:
            with open(outname) as json_file:
                self.response = json.load(json_file)

    def pull_questions(self):
        entries = []
        flag =False
        for block in self.response['Blocks']:
            if block['BlockType'] == 'LINE':
                box = block['Geometry']['BoundingBox']
                if flag and (block['Text'][0].isdigit() or block['Text'][:3]=='La.' or block['Text'] == 'Le. Middle Name' or block['Text'] == '5.') and '4.' not in block['Text']:
                    text = block['Text']
                    if text =='La. Family Name':
                       text = '1.a. Family Name'
                    elif text == 'Le. Middle Name':
                        text = '1.c. Middle Name'
                    elif text == '5.':
                        text = '5. Date of Birth (mm/dd/yyyy)'
                        box['Left'] = box['Left'] + .15
                    entries.append({'text': text, 'box':box})
                    print(text)
                elif 'Part 1' in block['Text']:
                    flag = True


        entries = sorted(entries, key = lambda i: i['text'])
        
        questions = []
        children = []
        main = entries[0]
        for entry in entries[1:]:
            if entry['text'] != '6.' or entry['text'] != '7.':
                qtype = 'text'
                questions.append({'main': main, 'children': children, 'qtype': qtype})
                main = entry

        questions.append({'main': main, 'children': children, 'qtype': qtype})
        self.questions = questions
        return questions
                
            
                


if  __name__ == '__main__':
    c = Controller('i485.png')
    questions = c.pull_questions()
    with open("i485.json", "w") as outfile:
        json.dump(questions, outfile)
        print('done')
