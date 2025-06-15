
from flask import Flask, render_template, request, redirect, session, url_for
import json, os, time
from gtts import gTTS

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            return json.load(file)
    return {}

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']

        users = load_users()
        if email in users:
            return 'Email already registered.'
        
        users[email] = {'name': name, 'password': password, 'coins': 0, 'gender': gender, 'logs': []}
        save_users(users)
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = load_users()
        user = users.get(email)
        if user and user['password'] == password:
            session['email'] = email
            return redirect('/dashboard')
        return 'Invalid login.'
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' not in session:
        return redirect('/login')
    
    users = load_users()
    user = users[session['email']]
    return render_template('dashboard.html', user=user)

@app.route('/speak', methods=['POST'])
def speak():
    if 'email' not in session:
        return redirect('/login')

    theme = request.form['theme']
    voice = request.form['voice']
    text = f"Welcome to the {theme} conversation! Let's begin."
    tts = gTTS(text=text, lang='en', tld='co.in' if voice == 'female' else 'com')
    filename = f'static/audio/{time.time()}.mp3'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    tts.save(filename)

    users = load_users()
    user = users[session['email']]
    user['coins'] += 1
    user['logs'].append({'time': time.ctime(), 'theme': theme})
    save_users(users)

    return render_template('dashboard.html', user=user, audio=filename)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
