import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from nose.tools import raises

from app2.libs.model import User, Base

class user_model_test(unittest.TestCase):
    '''
    although sqlalchemy support::
        Session = sessionmaker(bind=engine)
    however, I prefer to *late* bind the session and engine, so i use following code::
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
        self.engine = create_engine('sqlite:///:memory:', echo=True)
        Session = sessionmaker()
        Session.configure(bind=self.engine)  # once engine is available
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def test_constructor(self):
        user = User(username="username", password="password", email="username@domain.name")
        self.session.add(user)
        self.session.commit()
        new_insert_user = self.session.query(User).first()
        self.assertTrue(user is new_insert_user)

    def test_any_register_user_is_actvie_and_authenticated(self):
        user = User(username="username", password="password", email="username@domain.name")
        self.session.add(user)
        self.session.commit()
        new_insert_user = self.session.query(User).first()
        self.assertTrue(new_insert_user.is_active())
        self.assertTrue(new_insert_user.is_authenticated())

    @raises(IntegrityError)
    def test_two_users_have_same_username_is_prohibit(self):
        user = User(username="username", password="password", email="username@domain.name")
        self.session.add(user)
        self.session.commit()
        user = User(username="username", password="password1", email="username1@domain.name")
        self.session.add(user)
        self.session.commit()

    @raises(IntegrityError)
    def test_two_users_have_same_username_is_prohibit(self):
        user = User(username="username", password="password", email="username@domain.name")
        self.session.add(user)
        self.session.commit()
        user = User(username="username1", password="password1", email="username@domain.name")
        self.session.add(user)
        self.session.commit()

    def test_password_should_be_encryped_once_it_assign_to_model(self):
        user = User(username="username", password="password", email="username@domain.name")
        self.assertTrue(user.password != "password")
