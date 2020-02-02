from flask import Flask, render_template, make_response, jsonify, request, session, send_from_directory
from translator import translate_data, translate_questions, translate_phrase, translate_dict
import html
from PIL import Image, ImageDraw, ImageFont
from classifier import Classifier
import json
import os

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = "images"

ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg']

lower = 'abcdefghijklmno'

# fixes issue with old images being displayed
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/getQuestions/', methods=['GET'])
def get_questions():
    lang = request.args.get("lang")
    document = request.args.get("document")
    if document == 'upload':
        c = Classifier()
        questions = c.process('hashes/example.png')
        with open('upload.json', 'w') as outfile:
            json.dump(questions, outfile)
    else:
        questions = json.load(open('{}.json'.format(document), 'r'))

    if request.args.get('type') == 'json':
        return jsonify(questions)

    
    questions = translate_questions(questions, lang)

    
    placeholder = translate_phrase('Answer here', lang)
    
    a = ""
    for q in questions:
        if q['qtype'] == 'text' and len(q['children']) == 0:
            a += '''
            <div class="form-group">
            <label for="{}">{}</label>
            <input type="name" name="{}" class="form-control" placeholder="{}"></div>
            '''.format(q['main']['text'].split('.')[0], q['main']['text'], q['main']['text'].split('.')[0], placeholder)

        elif q['qtype'] == 'text':
            a += '''
            <div class="form-group">
            <label for="{}">{}</label><br>
            '''.format(q['main']['text'].split('.')[0], q['main']['text'])
            count = 0
            for s in q['children']:
                a += '''
                <div class="form-group">
                <label for="{}">{}</label>
                <input type="name" class="form-control" id="{}" placeholder="{}" name="{}"></div>
                '''.format(q['main']['text'].split('.')[0] + lower[count] + '. ', lower[count] + '. ' + s['text'], q['main']['text'].split('.')[0] + lower[count] + '. ', placeholder, q['main']['text'].split('.')[0] + lower[count])
                count += 1

            a += "</div>"

        elif q['qtype'] == 'radio':
            a += '''
            <label for="{}">{}</label>
            <div class="form-group form-inline" id ="{}">
            '''.format(q['main']['text'].split('.')[0], q['main']['text'], q['main']['text'].split('.')[0])
            count = 0
            for s in q['children']:
                a += '''
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="{}" id="Yes" value="{}" checked>
                    <label class="form-check-label" for="Yes">{}</label>
                </div>
                '''.format(q['main']['text'].split('.')[0], count, s['text'])

                count += 1
            a += "</div>"

        else:
            a += '''
            <p>{}</p>
            '''.format(q['main']['text'])
            for s in q['children']:
                a += '''
                <input type="checkbox" name="vehicle1" value="Bike">{}<br>
                '''.format(s['text'])

    a += """
        <input class="btn btn-primary" type="submit" value="Submit">
        """
    return a


@app.route('/formSubmit', methods=['GET', 'POST'])
def form_submit():
    if request.method == 'POST':
        answers = request.form.to_dict()
        #answers = translate_dict(answers, 'en')


        questions = json.load(open('{}.json'.format(session.get('document')), 'r'))

        for key in answers:
            if key[-1] not in lower:
                questions[int(key)-1]['answer'] = answers[key]
            else:
                questions[int(key[:-1])-1]['children'][lower.index(key[-1])]['answer'] = answers[key]
        

        
                
        im = Image.open('{}/{}.png'.format(app.config['UPLOAD_FOLDER'], session.get('document')))
        im = im.convert('RGBA')

        coordinates = questions[0]['main']['box']
        height = int(im.height*coordinates['Height'])

        text_layer = Image.new('RGBA', im.size, (255,255,255,0))
        fnt = ImageFont.truetype('arial.ttf', height)
        d = ImageDraw.Draw(text_layer)


        for question in questions:
            # textbox inputs no subfields
            if question['qtype'] == 'text' and len(question['children']) == 0:
                coordinates = question['main']['box']
                d.text((im.width*coordinates['Left'], im.height*coordinates['Top']+(height*1.4)), question['answer'], font=fnt, fill=(0,0,0,255))
            # texbox input w/ subfields
            elif question['qtype'] == 'text':
                for i in question['children']:
                   coordinates = i['box']
                   d.text((im.width*coordinates['Left'], im.height*coordinates['Top']+(height*1.4)), i['answer'], font=fnt, fill=(0,0,0,255))
            # radio button input
            elif question['qtype'] == 'radio':
                answer = question['answer']
                coordinates = question['children'][int(answer)]['box']
                d.text((im.width*coordinates['Left']-im.width*.025, im.height*coordinates['Top']),"X", font=fnt, fill=(0,0,0,255))
            

        out = Image.alpha_composite(im, text_layer)

        document = session.get('document')

        out.save('{}/{}1.png'.format(app.config['UPLOAD_FOLDER'], document))

        out = out.convert('RGB')
        out.save('{}/{}.pdf'.format(app.config['UPLOAD_FOLDER'], document))
        session.clear()
        return render_template('result.html', fileName='{}1.png'.format(document), dlFileName='{}.pdf'.format(document))
        
        
    return 'you are a failure'

@app.route('/document/<lang>')
def document_select(lang):
    data = [{'title':'I-589', 'body':'Complete the Application for Asylum and for Withholding of Removal', 'upload': 'Go'},
            {'title':'I-485', 'body':'Complete the Application to Register Permanent Residence or Adjust Status.', 'upload': 'Go'},
            {'title':'Other', 'body':'Complete a form different from the ones presented.', 'upload':'Upload'}]

    data = translate_data(data, lang)
    data[0]['url'] = '/i589/{}'.format(lang)
    data[1]['url'] = '/i485/{}'.format(lang)
    data[2]['url'] = '/upload/{}'.format(lang)

    for d in data:
        d['body'] = html.unescape(d['body'])

    return render_template("document.html", data=data)


@app.route('/forms/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/i589/<lang>')
def i589(lang):
    session['document'] = 'i589'      
    return render_template('form.html', lang=lang, document='i589')


@app.route('/i485/<lang>')
def i485(lang):
    session['document'] = 'i485'
    return render_template('form.html', lang=lang, document='i485')

@app.route('/upload/<lang>')
def upload(lang):
    session['document'] = 'upload'
    return render_template('form.html', lang=lang, document='upload')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()
