import json
import unittest
from discussion.utils.auth import decode_auth_token
from discussion.app import create_app, db
from discussion.tests.fixtures import user_fixture
from discussion.models.user import User
from flask import url_for


class UserViewsTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.reqctx = self.app.test_request_context()
        self.reqctx.push()
        db.drop_all()
        db.create_all()
    
    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.appctx.pop()
        self.reqctx.pop()

    def test_create_user(self):
        response = self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        self.assertEqual(response.status_code, 200)
    
    def test_create_duplicte_user(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        response = self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        self.assertEqual(response.status_code, 400)
        self.assertIn('code', response.json)

    def test_create_user_invalid_input(self):
        response = self.client.post(url_for('users.UserView'), json=user_fixture['dana_invalid'])
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.json)
    
    def test_valid_login(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        response = self.client.post(url_for('users.LoginView'), json=user_fixture['dana_valid'])
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(decode_auth_token(response.json['token']), User)
    
    def test_invalid_login(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        response = self.client.post(url_for('users.LoginView'), json=user_fixture['mamad_valid'])
        self.assertEqual(response.status_code, 401)
    
    def test_valid_logout(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        response = self.client.post(url_for('users.LoginView'), json=user_fixture['dana_valid'])
        token = 'token ' + response.json['token']
        response = self.client.get(url_for('users.LogOutView'), headers=[('Authorization', token),])
        self.assertEqual(response.status_code, 204)
        
    def test_invalid_logout(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        response = self.client.post(url_for('users.LoginView'), json=user_fixture['dana_valid'])
        token = response.json['token'][:-1]
        response = self.client.get(url_for('users.LogOutView'), headers=[('Authorization', token)])
        self.assertEqual(response.status_code, 401)
    
    def test_invalid_edit_user_details(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        token = 'token ' + self.client.post(url_for('users.LoginView'), json=user_fixture['dana_valid']).json['token']
        response = self.client.put(url_for('users.UserView'), headers=[('Authorization', token),], json=user_fixture['dana_invalid'])
        self.assertEqual(response.status_code, 422)
    
    def test_valid_edit_user_details(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        token = 'token ' + self.client.post(url_for('users.LoginView'), json=user_fixture['dana_valid']).json['token']
        response = self.client.put(url_for('users.UserView'), headers=[('Authorization', token),], json=user_fixture['dana_valid_edit'])
        self.assertEqual(response.status_code, 204)
    
    def test_delete_user(self):
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        token = 'token ' + self.client.post(url_for('users.LoginView'), json=user_fixture['dana_valid']).json['token']
        response = self.client.delete(url_for('users.UserView'), headers=[('Authorization', token),])
        self.assertEqual(response.status_code, 204)

    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)
        
    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_check('cat'))
        self.assertFalse(u.password_check('dog'))
    
    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)