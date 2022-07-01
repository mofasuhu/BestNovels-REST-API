from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
import pandas as pd
from flask_marshmallow import Marshmallow


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bestbooks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = True


db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


frame = pd.read_excel('books.xlsx',sheet_name='books')
book_num = frame['الترتيب'].count()

@app.cli.command('db_seed')
def db_seed():
    for i in range(book_num):
        i = Book(الرواية = frame['الرواية'].values[i],
                   صفحة_الرواية = frame['صفحة_الرواية'].values[i],
                   المؤلف = frame['المؤلف'].values[i],
                   صفحة_المؤلف = frame['صفحة_المؤلف'].values[i],
                   البلد = frame['البلد'].values[i],
                   صفحة_البلد = frame['صفحة_البلد'].values[i])
        db.session.add(i)
    db.session.commit()
    print('Database seeded!')


@app.route('/')
def hello():
    return jsonify(message='Hello from the Best Books API.'), 200


@app.route('/books', methods=['GET'])
def books():
    books_list = Book.query.all()
    result = books_schema.dump(books_list)
    return jsonify(result)


@app.route('/book/<int:id>', methods=["GET"])
def book(id: int):
    book = Book.query.filter_by(الترتيب=id).first()
    if book:
        result = book_schema.dump(book)
        return jsonify(result)
    else:
        return jsonify(message="That book does not exist!"), 404


@app.route('/add_book', methods=['POST'])
def add_book():
    الرواية = request.form['الرواية']
    test = Book.query.filter_by(الرواية=الرواية).first()
    if test:
        return jsonify("There is already a book by that name!"), 409
    else:
        صفحة_الرواية = request.form['صفحة_الرواية']
        المؤلف = request.form['المؤلف']
        صفحة_المؤلف = request.form['صفحة_المؤلف']
        البلد = request.form['البلد']
        صفحة_البلد = request.form['صفحة_البلد']
        new_book = Book(الرواية=الرواية,
                            صفحة_الرواية=صفحة_الرواية,
                            المؤلف=المؤلف,
                            صفحة_المؤلف=صفحة_المؤلف,
                            البلد=البلد,
                            صفحة_البلد=صفحة_البلد)
        db.session.add(new_book)
        db.session.commit()
        return jsonify(message="You added a book."), 201


@app.route('/update_book', methods=['PUT'])
def update_book():
    الترتيب = int(request.form['الترتيب'])
    book = Book.query.filter_by(الترتيب=الترتيب).first()
    if book:
        book.الرواية = request.form['الرواية']
        book.صفحة_الرواية = request.form['صفحة_الرواية']
        book.المؤلف = request.form['المؤلف']
        book.صفحة_المؤلف = request.form['صفحة_المؤلف']
        book.البلد = request.form['البلد']
        book.صفحة_البلد = request.form['صفحة_البلد']
        db.session.commit()
        return jsonify(message="You updated a book."), 202
    else:
        return jsonify(message="That book does not exist!"), 404


@app.route('/remove_book/<int:id>', methods=['DELETE'])
def remove_book(id: int):
    book = Book.query.filter_by(الترتيب=id).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify(message="You deleted a book."), 202
    else:
        return jsonify(message="That book does not exist"), 404


class Book(db.Model):
    __tablename__ = 'Best-Books'
    الترتيب = Column(Integer, primary_key=True)
    الرواية = Column(String)
    صفحة_الرواية = Column(String)
    المؤلف = Column(String)
    صفحة_المؤلف = Column(String)
    البلد = Column(String)
    صفحة_البلد = Column(String)


class BookSchema(ma.Schema):
    class Meta:
        fields = ('الترتيب',
                  'الرواية',
                  'صفحة_الرواية',
                  'المؤلف',
                  'صفحة_المؤلف',
                  'البلد',
                  'صفحة_البلد')


book_schema = BookSchema()
books_schema = BookSchema(many=True)


if __name__ == '__main__':
    app.run()
