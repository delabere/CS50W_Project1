from sqlalchemy import create_engine
import csv

# create database connection
engine = create_engine(
    "postgres://onfwzccdzpjzgo:25b3ec29ff230332eb948ca489d4fb22c9d3c00cc7a7cc8a723ea8c6f84de8dd@ec2-54-217-219-235.eu-west-1.compute.amazonaws.com:5432/dcig9roku03qke")
db = engine.connect()

# write data to database
with open('books.csv', 'r') as file:
    for i, row in enumerate(csv.reader(file), 1):
        if i > 1:  # skip header row
            isbn = row[0]
            title = row[1].replace("'", "''")   # escape single quotes
            author = row[2].replace("'", "''")  # escape single quotes
            year = int(row[3])
            db.execute(
                f"INSERT INTO books (isbn, title, author, year) VALUES ('{isbn}', '{title}', '{author}', {year})")
