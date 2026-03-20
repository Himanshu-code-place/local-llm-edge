from flask import Flask, render_template, request
import ollama

app = Flask(__name__)

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
    if request.method == 'POST':
        text = request.form['text']
        mode = request.form['mode']
        result = get_ai_response(text, mode)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)