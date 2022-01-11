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
        response = self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json, {
        #     'first_name': 'dana',
        #     'username': 'dana',
        #     'invitations_sent': [],
        #     'email': 'dana@dana.com',
        #     'id': 1,
        #     'last_name': 'danaplastiki',
        #     'created_discussions': [],
        #     'invitations_recived': [],
        #     'followed_discussions': [],
        #     'host_for': [],
        #     'participated_discussions': [],
        #     'participated_with_users': []
        # })
    
    def test_create_duplicte_user(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {
            "code": 400,
            "description": "Your input was invalid.",
            "name": "Bad Request"
        })

    def test_create_user_invalid_input(self):
        response = self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_invalid'])
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
    
    def test_valid_login(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(decode_auth_token(response.json['token']), User)
    
    def test_invalid_login(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('users.login_user'), json=user_fixture['user_mamad_valid'])
        self.assertEqual(response.status_code, 401)
    
    def test_valid_logout(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid'])
        token = 'token ' + response.json['token']
        response = self.client.post(url_for('users.logout_user'), headers=[('Authorization', token),])
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_logout(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid'])
        token = response.json['token'][:-1]
        response = self.client.post(url_for('users.logout_user'), headers=[('Authorization', token)])
        self.assertEqual(response.status_code, 401)

    def test_invalid_login_with_token(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        response = self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid'])
        token = 'token ' + response.json['token']
        response = self.client.post(url_for('users.login_user'), headers=[('Authorization', token),], json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 401)
    
    def test_get_empty_user_discussions(self):
        response = self.client.get(url_for('users.get_creator_discussions', user_id=2))
        self.assertEqual(response.json, {
        "count": 0,
        "discussions": [],
        "next": None,
        "prev": None
        })
    
    def test_invalid_edit_user_details(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        response = self.client.put(url_for('users.edit_user_detail'), headers=[('Authorization', token),], json=user_fixture['user_dana_invalid'])
        self.assertEqual(response.status_code, 400)
    
    def test_valid_edit_user_details(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        response = self.client.put(url_for('users.edit_user_detail'), headers=[('Authorization', token),], json=user_fixture['user_dana_valid_edit'])
        self.assertEqual(response.status_code, 200)
    
    def test_delete_user(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        response = self.client.delete(url_for('users.edit_user_detail'), headers=[('Authorization', token),])
        self.assertEqual(response.status_code, 200)
        
    def test_depricated_token_login_deleted_user(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        self.client.delete(url_for('users.edit_user_detail'), headers=[('Authorization', token),])
        response = self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 401)
    
    def test_depricated_token_login_logged_out_user(self):
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        self.client.post(url_for('users.logout_user'), headers=[('Authorization', token),])
        response = self.client.post(url_for('users.login_user'), headers=[('Authorization', token),], json=user_fixture['user_dana_valid'])
        self.assertEqual(response.status_code, 401)
        

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