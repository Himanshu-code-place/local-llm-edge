from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import ollama
import fitz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'local-llm-secret-key-2024'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password!"
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing = User.query.filter_by(username=username).first()
        if existing:
            error = "Username already exists!"
        else:
            hashed = generate_password_hash(password)
            user = User(username=username, password=hashed)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
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
                user_id=session['user_id'],
                mode=mode,
                input_text=input_text[:500],
                result=result
            )
            db.session.add(entry)
            db.session.commit()

    history = History.query.filter_by(
        user_id=session['user_id']
    ).order_by(History.created_at.desc()).limit(5).all()

    return render_template('index.html', result=result, error=error, history=history, mode=mode)

@app.route('/clear', methods=['POST'])
@login_required
def clear_history():
    History.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    return ('', 204)

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    total = History.query.filter_by(user_id=user_id).count()
    healthcare = History.query.filter_by(user_id=user_id, mode='healthcare').count()
    finance = History.query.filter_by(user_id=user_id, mode='finance').count()
    hindi = History.query.filter_by(user_id=user_id, mode='hindi').count()

    recent = History.query.filter_by(user_id=user_id).order_by(History.created_at.desc()).limit(10).all()
    dates = {}
    for item in recent:
        date = item.created_at.strftime('%d %b')
        dates[date] = dates.get(date, 0) + 1

    stats = {
        'total': total,
        'healthcare': healthcare,
        'finance': finance,
        'hindi': hindi,
        'dates': list(dates.keys()),
        'counts': list(dates.values())
    }

    history = History.query.filter_by(user_id=user_id).order_by(History.created_at.desc()).limit(8).all()
    return render_template('dashboard.html', stats=stats, history=history)

if __name__ == '__main__':
    app.run(debug=True)