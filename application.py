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
# session['authenticated'] = False


@app.route("/", methods=['GET', 'POST'])
@app.route("/<message>", methods=['GET', 'POST'])
def login(message='Welcome!'):
    if 'authenticated' in session:
        if session['authenticated'] == True:
            return(redirect(url_for('search')))
        else:
            if request.method == 'GET':
                return render_template('login.html', message=message)

            else:
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                              {'username': session['username'], 'password': session['password']}).fetchone() != None:
                    session['authenticated'] = True
                    return(redirect(url_for('search')))
                else:
                    return("Incorrect username or password - or the user doesn't exist")


@app.route("/logout")
def logout():
    session['authenticated'] = False
    return 'user logged out'


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']

        # check that user doesn't already exist
        if db.execute("SELECT * FROM users WHERE username = :username",
                      {'username': username}).fetchone() == None:
            db.execute("INSERT INTO USERS(username, password) values(:username, :password)",
                       {'username': username, 'password': password})
            db.commit()

        else:
            return('User already exists...please try another username')
        return redirect(url_for('login',
                                message="User created, please login!"))


@app.route("/search")
@app.route("/search/<isbn>")
def search(isbn=None):
    if 'authenticated' in session:
        return 'This is where the search page is going to go'
    else:
        return 'This area is only for users who have logged in'
