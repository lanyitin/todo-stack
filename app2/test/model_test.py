import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app2.libs.model import User, Base

class user_model_test(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', echo=True)
        '''
        although sqlalchemy support::
            Session = sessionmaker(bind=engine)
        however, i prefer to *late* bind the session and engine, so i use following code::
            Session = sessionmaker()
            Session.configure(bind=engine)  # once engine is available
        '''
        '''
            object dependency can be represented as following *->* means depend on
            session -> engine <- metadata
        '''
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
