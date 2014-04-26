# -*- coding: utf-8 -*-
import hashlib
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    '''
    Attributes:
        id (num): unique identifier number, only assigned by database

        username (str): the username, which is **unique** among all users, of this user.

        email (str): the email, which is **unique** as well among all users, of this user.

        __password__ (str): encrypted password that is stored in database.

        .. warning::
            do not directly access this property

        password (str): getter/setter of __password__, we perform encryption in this function.
    '''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable = False)
    email = Column(String(120), unique=True, nullable = False)
    __password__ = Column('password', String(120), nullable = False)

    @property
    def password(self):
        '''
        Parameters:
            password(str): plain text of password
        '''
        return self.__password__
    @password.setter
    def password(self, password):
        self.__password__ = hashlib.md5(password).hexdigest()

    def __init__(self, **argus):
        if 'id' in argus:
            self.id = unicode(argus['id'])
        self.username = argus['username']
        self.password = argus['password']
        self.email = argus['email']

    def is_authenticated(self):
        ''' used by flask-login '''
        return True

    def is_active(self):
        ''' used by flask-login '''
        return True

    def is_anonymous(self):
        ''' used by flask-login '''
        return False

    def get_id(self):
        ''' used by flask-login '''
        return self.id

# class Connection(Base):
#     __tablename__ = 'connection'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     provider_id = Column(String(255))
#     provider_user_id = Column(String(255))
#     access_token = Column(String(255))
#     secret = Column(String(255))
#     display_name = Column(String(255))
#     profile_url = Column(String(512))
# 
# tag_todo_assication = Table('tag_todo_association',
#     Column("todo_id", Integer, ForeignKey('todo.id'), nullable = False, primary_key=True),
#     Column("tag_id", Integer, ForeignKey('tag.id'), nullable = False, primary_key=True)
# )
# 
class Todo(Base):
    __tablename__ = 'todo'
    __table_args__ = ( UniqueConstraint('owner_user_id', 'order', 'in_trash'),)
    id = Column(Integer, primary_key=True)
    content = Column(Text(collation='utf8_general_ci'), nullable = False)
    push_date_time = Column(DateTime, nullable = False)
    '''
    an user cannot have two or more todos that have same order

    .. code::
        __table_args__ = ( UniqueConstraint('owner_user_id', 'order', 'in_trash'),)
    '''
    order = Column(Integer, nullable = False)
    priority = Column(Integer, default = 2, nullable = False)
    in_trash = Column(Boolean, default=False, nullable = False)
    owner_user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
    owner = relationship('User', backref = backref('todos', lazy='subquery'))

    # tags = relationship("Tag", secondary=tag_todo_assication, backref="todos")

    def __str__(self):
        return str({"id":self.id, "content":self.content, "order":self.order, "owner_user_id":self.owner_user_id, "priority":self.priority})
    def __repr__(self):
        return self.__str__()
    def __init__(self, content, owner):
        self.order = -1
        self.owner = owner
        self.push_date_time = datetime.utcnow()
        if len(str(content)) == 0:
            content = None
        self.content = content
# 
# class Tag(Base):
#     __tablename__ = 'tag'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(80, collation='utf8_general_ci'), unique=True, nullable = False)
# 
#     owner_user_id = Column(Integer, ForeignKey('user.id'), nullable = False)
#     owner = relationship('User', backref = backref('tags', lazy='dynamic'))
# 
#     def __str__(self):
#         return str({"id":self.id, "name":self.name})
#     def __repr__(self):
#         return self.__str__()
