import unittest
from app.facade import Facade

class facade_test(unittest.TestCase):
    def setUp(self):
        self.facade = Facade()

    def test_should_fail(self):
        self.assertTrue(False)
