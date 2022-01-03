import json
import unittest
from discussion.blueprints.utils import decode_auth_token

from discussion.app import create_app, db
from discussion.fixtures import user_fixture
from discussion.models.user import User
from flask import url_for


class UserAuthViewsTest(unittest.TestCase):

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
        db.drop_all()
        self.appctx.pop()
        self.reqctx.pop()

    def test_create_user(self):
        response = self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            'name': 'dana',
            'username': 'dana',
            'invitations_sent': [],
            'email': 'dana@dana.com',
            'id': 1,
            'lastname': 'danaplastiki',
            'created_discussions': [],
            'invitations_recived': [],
            'followed_discussions': [],
            'host_for': [],
            'participated_discussions': [],
            'participated_with_users': []
        })
    
    def test_create_duplicte_user(self):
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {
            "code": 400,
            "description": "Your input was invalid.",
            "name": "Bad Request"
        })

    def test_create_user_invalid_input(self):
        response = self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_invalid'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {
            "code": 400,
            "description": {
                "email": [
                    "Not a valid email address."
                ],
                "password": [
                    "Length must be between 8 and 24."
                ],
                "username": [
                    "Not a valid string."
                ]
            },
            "name": "Bad Request"
        })
    
    def test_user_valid_login(self):
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('auth.login_user'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(decode_auth_token(response.json['token']), User)
    
    def test_invalid_login(self):
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('auth.login_user'), json=user_fixture['user_mamad_valid'])
        self.assertEqual(response.status_code, 401)
    
    def test_valid_logout(self):
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('auth.login_user'), json=user_fixture['user_dana_valid'])
        token = 'token ' + response.json['token']
        response = self.client.post(url_for('auth.logout_user'), headers=[('Authorization', token),])
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_logout(self):
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('auth.login_user'), json=user_fixture['user_dana_valid'])
        token = response.json['token'][:-1]
        response = self.client.post(url_for('auth.logout_user'), headers=[('Authorization', token)])
        self.assertEqual(response.status_code, 401)

    def test_invalid_login_with_token(self):
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('auth.login_user'), json=user_fixture['user_dana_valid'])
        token = 'token ' + response.json['token']
        response = self.client.post(url_for('auth.login_user'), headers=[('Authorization', token),], json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 401)