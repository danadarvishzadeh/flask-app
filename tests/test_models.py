import unittest
import datetime
from discussion.models import User


class UserModelTestCase(unittest.TestCase):

    def test_no_password_getter(self):
        u = User(password='333')
        with self.assertRaises(ValueError):
            u.password
    
    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertIsNotNone(u.password_hash)

    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_check('cat'))
        self.assertFalse(u.password_check('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertNotEqual(u.password_hash, u2.password_hash)