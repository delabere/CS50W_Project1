import os
from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json

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


def get_results(search_term, search_field):
    """Returns database results as a list of tuples"""
    books = db.execute(f"SELECT * FROM books where ( LOWER({search_field}) LIKE '%' || :search_term || '%')",
                       {'search_term': search_term.lower()}).fetchall()
    print('==============================GETBOOKSS===========================')
    return books


def getBookdata(isbn):
    """Retrieves book data from the book table"""
    data = db.execute("SELECT * FROM books where isbn = :isbn",
                      {'isbn': isbn}).fetchone()
    return data


def getGrdsdata(isbn):
    """Retrieves book data from the goodreads API"""
    request_url = f"https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key=RloC1sRcAIRXYSD10c88AA"
    response = requests.get(request_url).json()
    ratings_count = response['books'][0]['work_ratings_count']
    average_rating = response['books'][0]['average_rating']
    return ratings_count, average_rating


def getReviews(isbn):
    """Gets review data from database"""
    review_data = db.execute("SELECT username, review_score, review_content FROM reviews where isbn = :isbn", {
                             'isbn': isbn}).fetchall()
    return review_data


@app.route("/", methods=['GET', 'POST'])
@app.route("/<message>", methods=['GET', 'POST'])
def login(message='Welcome!'):
    """View function to greet user with login screen"""
    message = 'Welcome!'
    if 'authenticated' in session:
        if session['authenticated'] == True:
            return(redirect(url_for('search')))
        else:
            if request.method == 'GET':
                return render_template('login.html', message=message, logout='false')
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
    """Allows the user to terminate the session"""
    session['authenticated'] = False
    del session['username']
    del session['password']
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    """View function that allows new users to register"""
    if request.method == 'GET':
        return render_template('register.html', logout='False', message='Register Here!')
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
            return render_template('register.html', logout='False', message='User already exists...please try another username')
        return redirect(url_for('login',
                                message="User created, please login!"))


@app.route("/search", methods=['GET', 'POST'])
def search(books=None, first=False):
    """Allows the search of books using isbn, title or author"""
    if 'authenticated' in session:
        if session['authenticated'] == True:
            if request.method == 'GET':
                return render_template('search.html', first=True)
            else:  # search functionality
                if request.form['isbn']:
                    books = get_results(
                        request.form['isbn'], search_field='isbn')
                    return render_template('search.html', books=books, first=False)
                elif request.form['title']:
                    books = get_results(
                        request.form['title'], search_field='title')
                    return render_template('search.html', books=books, first=False)
                elif request.form['author']:
                    books = get_results(
                        request.form['author'], search_field='author')
                    return render_template('search.html', books=books, first=False)
                else:
                    return render_template('search.html', first=False)
        else:
            return redirect(url_for('login', message='You have to login first!'))
    else:
        return redirect(url_for('login', message='You have to login first!'))


@app.route("/book/<isbn>", methods=['GET', 'POST'])
def book(isbn):
    """Gives user detail on a book and the abliity to rate it"""
    if request.method == 'GET':
        # ('158648303X', 'Auschwitz: A New History', 'Laurence Rees', 2005)
        _, title, author, year = getBookdata(isbn)
        ratings_count, average_rating = getGrdsdata(isbn)
        review_data = getReviews(isbn)
        return render_template('book.html', isbn=isbn, title=title,
                               author=author, year=year,
                               ratings_count=ratings_count,
                               average_rating=average_rating,
                               review_data=review_data)
    else:
        # add check that isbn is valid if entered manually else 404 error
        rating = request.form['rating']
        review = request.form['review']
        if 'username' in session:
            db.execute("INSERT INTO reviews(isbn, username, review_score, review_content) values(:isbn, :username, :review_score, :review_content)",
                       {'isbn': isbn, 'username': session['username'], 'review_score': rating, 'review_content': review})
            db.commit()
            return redirect(url_for('book', isbn=isbn))
        else:
            return redirect(url_for('login'))


@app.route('/api/<isbn>')
def api(isbn):
    """Returns a JSON response object from an api call"""
    response = {}
    # get the goodreads api data
    response['isbn'], response['title'], response['author'], response['year'] = getBookdata(
        isbn)
    response['review_count'], response['average_score'] = getGrdsdata(isbn)

    return json.dumps(response)
