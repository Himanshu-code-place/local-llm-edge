from flask import Flask, render_template, request
import ollama
import fitz
import os

app = Flask(__name__)

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
    else:
        system_prompt = "You are a financial analyst. Analyze the given text in 3 sections: 1. Main Points 2. Key Highlights 3. Conclusion. Be concise and professional."

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

    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)