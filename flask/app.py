from flask import Flask, render_template, make_response, jsonify
from translator import translate_data
app = Flask(__name__)

@app.route('/document/<lang>')
def document_select(lang):
    data = [{'title':'I-589', 'body':'Complete the Application for Asylum and for Withholding of Removal', 'upload': 'Go'},
            {'title':'I-485', 'body':'Complete the Application to Register Permanent Residence or Adjust Status.', 'upload': 'Go'},
            {'title':'Other', 'body':'Complete a form different from the ones presented.', 'upload':'Upload'}]

    data = translate_data(data, lang)

    return render_template("document.html", data=data)

@app.route('i-589/<lang>')
def i589(lang):
    


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
