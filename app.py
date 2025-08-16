from flask import Flask, render_template, redirect, url_for, request
import os
import json

app = Flask(__name__)

class Book:
    def __init__(self, title, author, genre, status="available"):
        self.title = title
        self.author = author
        self.genre = genre
        self.status = status

    def borrow(self):
        if self.status == "available":
            self.status = "borrowed"
            return True
        return False

    def return_book(self):
        if self.status == "borrowed":
            self.status = "available"
            return True
        return False

    def to_dict(self):
        return {"title": self.title, "author": self.author, "genre": self.genre, "status": self.status}

    @staticmethod
    def from_dict(data):
        return Book(data['title'], data['author'], data['genre'], data['status'])

class Library:
    def __init__(self, filepath):
        self.filepath = filepath
        self.books = self.load_books()

    def load_books(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    return [Book.from_dict(item) for item in data]
            except Exception as e:
                print("Error loading books:", e)
        return []

    def save_books(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump([book.to_dict() for book in self.books], f)
        except Exception as e:
            print("Error saving books:", e)

    def add_book(self, title, author, genre):
        self.books.append(Book(title, author, genre))
        self.save_books()

    def borrow_book(self, index):
        try:
            if self.books[index].borrow():
                self.save_books()
                return True
        except IndexError:
            pass
        return False

    def return_book(self, index):
        try:
            if self.books[index].return_book():
                self.save_books()
                return True
        except IndexError:
            pass
        return False
    

    def remove_book(self, index):
        try:
            self.books.pop(index)
            self.save_books()
        except IndexError:
            pass

# Initialize Library
library = Library("books.txt")

@app.route('/')
def index():
    return render_template('index.html', books=library.books)

@app.route('/add', methods=['POST'])
def add_book():
    try:
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        library.add_book(title, author, genre)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error adding book: {e}", 500

@app.route('/borrow/<int:index>')
def borrow_book(index):
    if library.borrow_book(index):
        return redirect(url_for('index'))
    return "Sorry, the book is already borrowed or index is invalid", 400

@app.route('/return/<int:index>')
def return_book(index):
    if library.return_book(index):
        return redirect(url_for('index'))
    return "Sorry, the book is not borrowed or index is invalid", 400

@app.route('/remove/<int:index>')
def remove_book(index):
    library.remove_book(index)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
