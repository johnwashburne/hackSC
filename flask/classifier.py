from PIL import Image
import imagehash
import boto3
import os
import json



class Classifier:

    def __init__(self):
        self.hashes = [imagehash.average_hash(Image.open('hashes/grid.png')), imagehash.average_hash(Image.open('hashes/essay.png'))]

    def compare(self, filepath):
        min_ = 100000000000
        index = -1
        new_hash = imagehash.average_hash(Image.open(filepath))
        i=0
        for hash_ in self.hashes:
            if hash_ - new_hash < min_:
                min_ = hash_ - new_hash
                index = i
            i += 1

        return index

    def process(self, filepath):

        index = self.compare(filepath)
        if index == 1:
            questions = self.process_essay(filepath)
        else:
            questions = self.process_grid(filepath)

        return questions

    def process_essay(self, filepath):
        response = self.textract(filepath)

        entries = []
        for block in response['Blocks']:
            if block['BlockType'] == "LINE":
                box = block['Geometry']['BoundingBox']
                entries.append({'text': block['Text'], 'box': box})

        questions = []
        children = []
        main = entries[0]
        main['text'] = '1. ' + main['text'][3:]
        qtype = 'radio'

        for line in entries[1:]:
            if line['text'] != 'No' and line['text'] != 'Yes':
                questions.append({'main': main, 'children': children, 'qtype': qtype})
                children = []
                main = line
            else:
                children.append(line)

        main['text'] = '2. ' + main['text']
        main['box']['Top'] += .02
        main['box']['Left'] += .02
        questions.append({'main': main, 'children': children, 'qtype': 'text'})

        return questions

    def process_grid(self, filepath):
        response = self.textract(filepath)

        entries = []
        for block in response['Blocks']:
            if block['BlockType'] == "LINE":
                box = block['Geometry']['BoundingBox']
                entries.append({'text': block['Text'], 'box': box})

        questions = []
        children = []
        main = entries[0]
        qtype = 'text'

        for line in entries[1:]:
            if line['text'][0].isdigit():
                questions.append({'main':main, 'children': children, 'qtype': qtype})
                children = []
                main = line
            else:
                children.append(line)

        questions.append({'main':main, 'children': children, 'qtype': qtype})
        return questions
      

        

    def textract(self, filename):
        with open(filename, 'rb') as document:
            image_bytes = bytearray(document.read())

        textract = boto3.client('textract', region_name='us-east-1',
                                aws_access_key_id='AKIAJOZSX5OBM2FX4G2Q',
                                aws_secret_access_key='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')

        response = textract.detect_document_text(Document={'Bytes': image_bytes})

            

        return response

        
        

if __name__ == "__main__":
    c = Classifier()
    print(c.process("hashes/example.png"))
