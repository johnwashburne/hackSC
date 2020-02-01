from flask import Flask, render_template, make_response, jsonify, request
from translator import translate_data, translate_questions
import json
app = Flask(__name__)

@app.route('/getQuestions/', methods=['GET'])
def get_questions():
    lang = request.args.get("lang")
    document = request.args.get("document")    
    questions = json.load(open('{}.json'.format(document), 'r'))
    questions = translate_questions(questions, lang)
    
    a = '<form action="/formSubmit" method="post">'
    for q in questions:
        if q['qtype'] == 'text' and len(q['children']) == 0:
            a += '''
            <p>{}</p>
            <input type="text" name="{}"><br>
            '''.format(q['main']['text'], q['main']['text'].split('.')[0])

        elif q['qtype'] == 'text':
            a += '''
            <p>{}</p>
            '''.format(q['main']['text'])
            for s in q['children']:
                a += '''
                <p>\t{}</p>
                \t<input type="text" name="firstname"><br>
                '''.format(s['text'])

        elif q['qtype'] == 'radio':
            a += '''
            <p>{}</p>
            '''.format(q['main']['text'])
            for s in q['children']:
                a += '''
                <input type="radio" name="{}" value="{}">{}<br>
                '''.format(q['main']['text'].split('.')[0], s['text'], s['text'])

        else:
            a += '''
            <p>{}</p>
            '''.format(q['main']['text'])
            for s in q['children']:
                a += '''
                <input type="checkbox" name="vehicle1" value="Bike">{}<br>
                '''.format(s['text'])

    a += """
        <input type="submit" value="Submit">
        </form>"""

    return a

@app.route('/formSubmit', methods=['GET', 'POST'])
def form_submit():
    

@app.route('/document/<lang>')
def document_select(lang):
    data = [{'title':'I-589', 'body':'Complete the Application for Asylum and for Withholding of Removal', 'upload': 'Go'},
            {'title':'I-485', 'body':'Complete the Application to Register Permanent Residence or Adjust Status.', 'upload': 'Go'},
            {'title':'Other', 'body':'Complete a form different from the ones presented.', 'upload':'Upload'}]

    data = translate_data(data, lang)

    return render_template("document.html", data=data)

@app.route('/i589/<lang>')
def i589(lang):
    
            
    return render_template('test.html', lang=lang)
        


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
