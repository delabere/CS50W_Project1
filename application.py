import os

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def get_results(search_term):
    books = db.execute("SELECT * FROM books where ( LOWER(isbn) LIKE '%' || :search_term || '%') OR (LOWER(title) LIKE '%' || :search_term || '%') OR (LOWER(author) LIKE '%' || :search_term || '%')",
                       {'search_term': search_term.lower()}).fetchall()
    print('===============================================GETBOOKSS=========================')
    return books


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
                    return redirect(url_for('login', message="Wrong username or password. Try again"))
    else:
        session['authenticated'] = False
        return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session['authenticated'] = False
    return redirect(url_for('login'))


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


@app.route("/search", methods=['GET', 'POST'])
def search(books=None, first=False):
    if 'authenticated' in session:
        if session['authenticated'] == True:
            if request.method == 'GET':
                return render_template('search.html', first=True)
            else:  # search functionality
                if request.form['isbn']:
                    books = get_results(request.form['isbn'])
                    return render_template('search.html', books=books, first=False)
                elif request.form['title']:
                    books = get_results(request.form['title'])
                    return render_template('search.html', books=books, first=False)
                elif request.form['author']:
                    books = get_results(request.form['author'])
                    return render_template('search.html', books=books, first=False)
                else:
                    return render_template('search.html', first=False)
        else:
            return redirect(url_for('login', message='You have to login first!'))
    else:
        return redirect(url_for('login', message='You have to login first!'))


@app.route("/book/<isbn>", methods=['GET', 'POST'])
def book(isbn):
    if request.method == 'GET':
        return render_template('book.html', isbn=isbn)
    else:
        # add check that isbn is valid if entered manually else 404 error
        rating = request.form['rating']
        review = request.form['review']
        print(rating, review)
        return render_template('book.html', isbn=isbn)
