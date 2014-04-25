import unittest
# from app.facade import Facade

@unittest.skip("")
class facade_test(unittest.TestCase):
    def setUp(self):
        self.facade = Facade()

    @unittest.skip('please refer docstring')
    def test_register(self):
        user = self.facade.register("username1", "password1", "username@domain.name")
        self.assertTrue(user is not None)
        '''
        cause facade is strong coupled with flask-sqlalchemy!!!
        we need to decouple it before we do any test
        .. todo::
            rewrite core model in pure sqlalchemy
        '''
