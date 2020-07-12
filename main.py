from flask import Flask, render_template, request, make_response, redirect, url_for
import hashlib
from models import db, User
import random
import uuid

app = Flask(__name__)
db.create_all()

@app.route("/")
def index():

    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter_by(email=email).first()

    secret_number = random.randint(1, 30)

    if not user:
        user = User(email=email, name=name, password=hashed_password, secret_number=secret_number)

        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return "Oh, somebody forgot their own password again. Try again "
    elif hashed_password == user.password:
        session_token = str(uuid.uuid4())

        user.session_token = session_token
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", session_token, httponly=True, samesite="strict")

    return response


@app.route("/result", methods=["POST"])
def result():

    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")


    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_number:
        message = f"Congratulations {user.name}, you've guessed it, the secret number was {user.secret_number}. A new secret number was set."

        new_secret_number = random.randint(1, 30)

        user.secret_number = new_secret_number

        db.add(user)
        db.commit()

    elif guess > user.secret_number:
        message = f"Your guess is too high. Try again with a smaller number."
    else:
        message = f"Your guess is too low. Try again with a bigger number."

    return render_template("result.html", message=message)

@app.route("/signout")
def signout():

    response = make_response(redirect(url_for("index")))
    response.set_cookie("session_token", "deleted", max_age=0)

    return response
