from flask import Flask, render_template, make_response, jsonify, request
from translator import translate_data, translate_questions, translate_phrase
import json
app = Flask(__name__)

lower = 'abcdefg'

@app.route('/getQuestions/', methods=['GET'])
def get_questions():
    lang = request.args.get("lang")
    document = request.args.get("document")
    
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
            <input type="name" name="{}" class="form-control" id="{}" placeholder="{}"></div>
            '''.format(q['main']['text'].split('.')[0], q['main']['text'], q['main']['text'].split('.')[0], q['main']['text'].split('.')[0], placeholder)
            

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
                    <input class="form-check-input" type="radio" name="{}" id="Yes" value="{}">
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
        answers = request.form
        for key in answers:
            answers 
        return request.form
    return 'you are a failure'

@app.route('/document/<lang>')
def document_select(lang):
    data = [{'title':'I-589', 'body':'Complete the Application for Asylum and for Withholding of Removal', 'upload': 'Go'},
            {'title':'I-485', 'body':'Complete the Application to Register Permanent Residence or Adjust Status.', 'upload': 'Go'},
            {'title':'Other', 'body':'Complete a form different from the ones presented.', 'upload':'Upload'}]

    data = translate_data(data, lang)
    data[0]['url'] = '/i589/{}'.format(lang)
    data[1]['url'] = '/i485/{}'.format(lang)
    data[2]['url'] = '/upload'

    return render_template("document.html", data=data)

@app.route('/i589/<lang>')
def i589(lang):
    
            
    return render_template('form.html', lang=lang)

@app.route('/form')
def form():
    return render_template('form.html')
        


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
