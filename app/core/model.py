from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://lanyitin:jiun7892@localhost/stacktodos?collation=utf8_general_ci&use_unicode=true&charset=utf8'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80, collation='utf8_general_ci'), unique=True)
    email = db.Column(db.String(120, collation='utf8_general_ci'), unique=True)
    password = db.Column(db.String(120, collation='utf8_general_ci'), unique=True)

class TagTodoAssication(db.Model):
    __tablename__ = 'tag_todo_association'
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    push_date = db.Column(db.DateTime)
    order = db.Column(db.Integer)
    priority = db.Column(db.Integer)

    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('user', backref = db.backref('todos', lazy='dynamic'))

    tags = db.relationship("tag", secondary=TagTodoAssication, backref="todos")

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80, collation='utf8_general_ci'), unique=True)

if __name__ is '__main':
    db.create_all()
