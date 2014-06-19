# pylint: disable=R0904, C0103, C0111, C0301, W0511

import unittest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from nose.tools import raises
from ..libs.model import User, Todo, Base, InvalidateRequiredCloclException


class DatabaseTestCase(unittest.TestCase):
    '''
    although sqlalchemy support::
        Session = sessionmaker(bind=engine)
    however, I prefer to *late* bind the session and engine,
    so i use following code::
        Session = sessionmaker()
        Session.configure(bind=engine)  # once engine is available
    '''
    '''
        object dependency can be represented as following *->* means depend on
    new_insert_user = self.session.query(User).first()
    self.assertTrue(user is new_insert_user)
        session -> engine <- metadata
    '''
    def setUp(self):
        db_connection_str = 'mysql+mysqlconnector://{0}:{1}@{2}:{3}' \
            '/stacktodos?collation=utf8_general_ci' \
            '&use_unicode=true&charset=utf8'
        sqlalchemy_database_uri = db_connection_str.format(
            os.environ['STACKTODOS_MYSQL_DB_USERNAME'],
            os.environ['STACKTODOS_MYSQL_DB_PASSWORD'],
            os.environ['STACKTODOS_MYSQL_DB_HOST'],
            os.environ['STACKTODOS_MYSQL_DB_PORT'],
        )
        self.engine = create_engine(sqlalchemy_database_uri, echo=False)
        make_session = sessionmaker()
        make_session.configure(bind=self.engine)  # once engine is available
        self.session = make_session()
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)


class user_model_test(DatabaseTestCase):

    def test_constructor(self):
        user = User(
            username="username1",
            password="password1",
            email="username1@domain.name"
        )
        self.session.add(user)
        self.session.commit()
        new_insert_user = self.session.query(User).first()
        self.assertTrue(user is new_insert_user)

    def test_any_register_user_is_actvie_and_authenticated(self):
        user = User(
            username="username1",
            password="password1",
            email="username1@domain.name"
        )
        self.session.add(user)
        self.session.commit()
        new_insert_user = self.session.query(User).first()
        self.assertTrue(new_insert_user.is_active())
        self.assertTrue(new_insert_user.is_authenticated())

    @raises(IntegrityError)
    def test_two_users_have_same_username_is_prohibit(self):
        user = User(
            username="username1",
            password="password1",
            email="username1@domain.name"
        )
        self.session.add(user)
        self.session.commit()
        user = User(
            username="username1",
            password="password2",
            email="username2@domain.name"
        )
        self.session.add(user)
        self.session.commit()

    def test_password_should_be_encryped_once_it_assign_to_model(self):
        user = User(
            username="username1",
            password="password1",
            email="username1@domain.name"
        )
        self.assertTrue(user.password != "password")


class tag_test(DatabaseTestCase):
    def setUp(self):
        super(tag_test, self).setUp()
        user = User(
            username="username1",
            password="password1",
            email="username1@domain.name"
        )
        self.session.add(user)
        self.session.commit()
        self.user = self.session.query(User).first()

    def test_constructor(self):
        tag = Todo(content="Hello World", owner=self.user, required_clock=3)
        self.session.add(tag)
        self.session.commit()
        tag = self.session.query(Todo).filter_by(owner=self.user).first()
        self.assertTrue(tag is not None)
        self.assertTrue(tag.content == "Hello World")

    @raises(IntegrityError)
    def test_content_cannot_be_empty_string(self):
        tag = Todo(content="", owner=self.user, required_clock=3)
        self.session.add(tag)
        self.session.commit()

    @raises(IntegrityError)
    def test_a_user_cannot_have_two_todos_that_have_same_order(self):
        todo = Todo(content="123", owner=self.user, required_clock=3)
        self.session.add(todo)
        todo = Todo(content="321", owner=self.user, required_clock=3)
        self.session.add(todo)
        self.session.commit()

    @raises(IntegrityError)
    def test_a_user_cannot_have_two_todos_that_have_same_order_even_in_trash(self):
        todo = Todo(content="123", owner=self.user, required_clock=3)
        todo.in_trash = True
        self.session.add(todo)
        todo = Todo(content="321", owner=self.user, required_clock=3)
        self.session.add(todo)
        self.session.commit()
        todo.in_trash = True
        self.session.add(todo)
        self.session.commit()


class todo_test(DatabaseTestCase):

    @raises(InvalidateRequiredCloclException)
    def test_required_clock_can_not_less_than_zero(self):
        user = User(
            username="username1",
            password="password1",
            email="username1@domain.name"
        )
        self.session.add(user)
        self.session.commit()
        Todo(content="123", owner=user, required_clock=-1)
