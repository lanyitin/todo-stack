# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, **argus):
        if 'id' in argus:
            self.id = unicode(argus['id'])
        self.username = argus['username']
        self.password = argus['password']
        self.email = argus['email']

    # used by flask-login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))


tag_todo_assication = db.Table(
    'tag_todo_association',
    db.Column(
        "todo_id",
        db.Integer,
        db.ForeignKey('todo.id'),
        nullable=False,
        primary_key=True
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey('tag.id'),
        nullable=False,
        primary_key=True
    ),
)


class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(collation='utf8_general_ci'), nullable=False)
    push_date_time = db.Column(db.DateTime, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, default=2, nullable=False)
    in_trash = db.Column(db.Boolean, default=False, nullable=False)

    owner_user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
    owner = db.relationship(
        'User',
        backref=db.backref('todos', lazy='subquery'),
    )

    tags = db.relationship(
        "Tag",
        secondary=tag_todo_assication,
        backref="todos"
    )

    def __str__(self):
        return str({
            "id": self.id,
            "content": self.content,
            "order": self.order,
            "owner_user_id": self.owner_user_id,
            "priority": self.priority,
            "tags":  self.tags,
        })

    def __repr__(self):
        return self.__str__()

    def __init__(self, content, owner_user_id):
        self.owner_user_id = owner_user_id
        self.push_date_time = datetime.utcnow()
        self.content = content


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(80, collation='utf8_general_ci'),
        unique=True,
        nullable=False,
    )

    owner_user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
    )
    owner = db.relationship('User', backref=db.backref('tags', lazy='dynamic'))

    def __str__(self):
        return str({"id": self.id, "name": self.name})

    def __repr__(self):
        return self.__str__()
