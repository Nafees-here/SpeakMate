from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from gtts import gTTS
from datetime import datetime
app = Flask(__name__)
app.secret_key = "speakmate_secret"

with open("users.json", "r") as f:
    users = json.load(f)

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email in users and users[email]["password"] == password:
            session["email"] = email
            return redirect(url_for("dashboard"))
        return "Invalid login."
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        gender = request.form["gender"]
        if email not in users:
            users[email] = {"name": name, "password": password, "gender": gender, "coins": 0, "progress": []}
            save_users()
            return redirect(url_for("home"))
        return "User already exists."
    return render_template("signup.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "email" not in session:
        return redirect(url_for("home"))
    email = session["email"]
    user = users[email]
    if request.method == "POST":
        message = request.form["message"]
        theme = request.form["theme"]
        voice_gender = request.form["voice"]
        coins_earned = 1
        user["coins"] += coins_earned
        user["progress"].append({"time": datetime.now().isoformat(), "message": message, "theme": theme})
        save_users()
        response = f"You said in {theme} theme: {message}"
        tts = gTTS(response, lang="en", tld="co.in" if voice_gender == "male" else "com.au")
        filename = f"static/audio/{email.replace('@', '_')}.mp3"
        tts.save(filename)
        return render_template("dashboard.html", user=user, audio_file=filename, message=message)
    return render_template("dashboard.html", user=user, audio_file=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
