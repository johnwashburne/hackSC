from flask import Flask, render_template, make_response, jsonify
import controller
app = Flask(__name__)



@app.route('/getData/<filename>', methods=['GET'])
def get_data(filename):
    c = controller.Controller(filename)
    return jsonify(c.get_questions())

@app.route('/getData2/<filename>', methods=['GET'])
def get_data2(filename):
    c = controller.Controller(filename)

    a = ""
    for q in c.get_questions():
        if q['qtype'] == 'text' and len(q['children']) == 0:
            a += """
            <p>{}</p>
            <input type="text" name=""><br>
            """.format(q['main']['text'])

    return a

@app.route('/')
def index():
    
    return render_template('test2.html')

if __name__ == "__main__":
    app.run()
