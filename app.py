from flask import Flask, flash, render_template, request, redirect, url_for, jsonify

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from database_setup import Book, Base

from flask_marshmallow import Marshmallow


# Init app
app = Flask(__name__)

# Database
engine = create_engine('sqlite:///books-collection.db', connect_args={'check_same_thread': False})
Base.metadata.bind = create_engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
ma = Marshmallow(app)
app.secret_key = "la_cookie"

# Books Schema
class BooksSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'genre')

# Init schema
books_schema = BooksSchema(many=True)


# Show all books
@app.route('/')
def showBooks():
    books = session.query(Book).all()
    if not books:
        flash('Add some books to start your collection!')
    return render_template("books.html", books=books)


# Add new book
@app.route('/', methods=['GET', 'POST'])
def newBook():
    if request.method == 'POST':
        if request.form['name'] and request.form['author']:
            newBook = Book(
            title = request.form['name'],
            author = request.form['author'],
            genre = request.form['genre']
            )
            session.add(newBook)
            session.commit()
            flash('New book added')
            return redirect(url_for('showBooks'))
        else:
            flash('Need to enter at least Title and Author of the book')
            return redirect(url_for('showBooks'))


# Edit book
@app.route('/<int:book_id>/edit/', methods=['GET', 'POST'])
def editBook(book_id):
    editedBook = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedBook.title = request.form['name']
            editedBook.author = request.form['author']
            editedBook.genre = request.form['genre']
            flash('Book edited successfully')
            return redirect(url_for('showBooks'))


#Delete book
@app.route('/<int:book_id>/delete/', methods=['GET', 'POST'])
def deleteBook(book_id):
    bookToDelete = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash('Book deleted')
        return redirect(url_for('showBooks'))


# API Get all books
@app.route('/api/all-books', methods=['GET'])
def get_all_books():
    all_books = session.query(Book).all()
    return books_schema.jsonify(all_books)


if __name__ == '__main__':
    app.run(debug=True)
