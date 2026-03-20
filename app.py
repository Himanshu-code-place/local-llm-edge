from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import ollama
import fitz
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(50))
    input_text = db.Column(db.Text)
    result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def extract_text_from_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def get_ai_response(text, mode):
    if mode == "healthcare":
        system_prompt = "You are a clinical documentation assistant. Summarise patient notes in exactly 3 sections: 1. Chief Complaint 2. Assessment 3. Plan. Be concise."
    elif mode == "finance":
        system_prompt = "You are a financial analyst. Analyze the given text in 3 sections: 1. Main Points 2. Key Highlights 3. Conclusion. Be concise and professional."
    else:
        system_prompt = "You are a helpful assistant. Analyze the given text in 3 sections: 1. Main Points 2. Key Highlights 3. Conclusion. Reply in Hindi language only."

    response = ollama.chat(
        model='llama3.2',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ]
    )
    return response['message']['content']

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    error = None
    input_text = ""
    mode = "healthcare"

    if request.method == 'POST':
        mode = request.form['mode']
        pdf_file = request.files.get('pdf_file')

        if pdf_file and pdf_file.filename.endswith('.pdf'):
            input_text = extract_text_from_pdf(pdf_file)
            if len(input_text.strip()) == 0:
                error = "PDF mein koi text nahi mila!"
            else:
                result = get_ai_response(input_text[:3000], mode)
        else:
            input_text = request.form.get('text', '')
            if len(input_text.strip()) == 0:
                error = "Please enter some text!"
            else:
                result = get_ai_response(input_text, mode)

        if result:
            entry = History(
                mode=mode,
                input_text=input_text[:500],
                result=result
            )
            db.session.add(entry)
            db.session.commit()

    history = History.query.order_by(History.created_at.desc()).limit(5).all()
    return render_template('index.html', result=result, error=error, history=history, mode=mode)

@app.route('/clear', methods=['POST'])
def clear_history():
    History.query.delete()
    db.session.commit()
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)