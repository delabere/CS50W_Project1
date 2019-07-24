import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
# postgres://onfwzccdzpjzgo:25b3ec29ff230332eb948ca489d4fb22c9d3c00cc7a7cc8a723ea8c6f84de8dd@ec2-54-217-219-235.eu-west-1.compute.amazonaws.com:5432/dcig9roku03qke

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@app.route("/<message>")
def login(message='Welcome!'):
    return render_template('login.html', message=message)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db.execute("INSERT INTO USERS (username, password) values (:username, :password)",
                   {'username': username, 'password': password})
        db.commit()
        return redirect(url_for('login', message="User created, please login!"))
    else:
        return render_template('register.html')
