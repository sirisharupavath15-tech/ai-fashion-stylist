from flask import Flask, render_template, request, redirect, session
import sqlite3
import cv2
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "fashion_secret"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------- DATABASE --------
def create_table():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
    )
    """)

    conn.commit()
    conn.close()

create_table()


# -------- SKIN TONE --------
def detect_skin_tone(image_path):

    img = cv2.imread(image_path)
    img = cv2.resize(img,(200,200))

    avg_color = img.mean(axis=0).mean(axis=0)

    r,g,b = avg_color

    if r > 180:
        tone = "Light"
    elif r > 130:
        tone = "Medium"
    else:
        tone = "Dark"

    return tone


# -------- LOGIN PAGE --------
@app.route("/")
def login():
    return render_template("login.html")


# -------- LOGIN CHECK --------
@app.route("/login", methods=["POST"])
def login_check():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    user = cur.fetchone()

    conn.close()

    if user:
        session["user"] = username
        return redirect("/upload")
    else:
        return "Invalid Login"


# -------- REGISTER PAGE --------
@app.route("/register")
def register():
    return render_template("register.html")


# -------- REGISTER USER --------
@app.route("/register_user", methods=["POST"])
def register_user():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))

    conn.commit()
    conn.close()

    return redirect("/")


# -------- UPLOAD PAGE --------
@app.route("/upload")
def upload():

    if "user" not in session:
        return redirect("/")

    return render_template("upload.html")


# -------- ANALYZE IMAGE --------
@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["photo"]
    gender = request.form["gender"]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    tone = detect_skin_tone(filepath)

    return render_template("result.html", tone=tone, gender=gender)


# -------- SHOP PAGE --------
@app.route("/shop")
def shop():

    gender = request.args.get("gender")
    tone = request.args.get("tone")

    return render_template("shop.html", gender=gender, tone=tone)


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)