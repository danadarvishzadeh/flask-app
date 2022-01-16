import unittest
from discussion.app import create_app
from discussion.extentions import db
from discussion.tests.fixtures import user_fixture, discussion_fixture
from flask import url_for
import logging


logger = logging.getLogger(__name__)
class TestUserAuthentication(unittest.TestCase):

    def setUp(self):
        app = create_app(config_name='testing')
        self.client = app.test_client()
        self.appctx = app.app_context()
        self.appctx.push()
        self.reqctx = app.test_request_context()
        self.reqctx.push()
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        self.client.post(url_for('users.UserView'), json=user_fixture['mamad_valid'])
        db.drop_all()
        db.create_all()
        
    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.appctx.pop()
        self.reqctx.pop()

    def test_authentication_endpoint(self):
        response = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)
    
    def test_refresh_token(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json
        response = self.client.post(url_for('users.RefreshTokenView'),
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)

    def test_access_protected_views(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json
        self.client.post(url_for('discussions.DiscussionView'),
                                    json=discussion_fixture['dana_first_discussion_valid'],
                                    headers=[('Authorization', tokens['access_token'])])
        response = self.client.get(url_for('invites.InvitationView'),
                                    discussion_id=1,
                                    headers=[('Authorization', tokens['access_token'])])
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url_for('invites.InvitationView'),
                                    discussion_id=1,
                                    headers=[('Authorization', 'wrong token.')])
        self.assertEqual(response.status_code, 403)
    
    def test_using_old_refresh_token(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json
        new_tokens = self.client.post(url_for('users.RefreshTokenView'),
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    })
        response = self.client.post(url_for('users.RefreshTokenView'),
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    })
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url_for('invites.InvitationView'),
                                    discussion_id=1,
                                    headers=[('Authorization', tokens['access_token'])])

        self.assertEqual(response.status_code, 403)

        response = self.client.get(url_for('invites.InvitationView'),
                                    discussion_id=1,
                                    headers=[('Authorization', new_tokens['access_token'])])

        self.assertEqual(response.status_code, 403)
    
    def test_revoke_access_token(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json
        self.client.get(url_for('users.LogoutView'),
                                    headers=[('Authorization', new_tokens['access_token'])])
        response = self.client.post(url_for('users.RefreshTokenView'),
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    })
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url_for('invites.InvitationView'),
                                    discussion_id=1,
                                    headers=[('Authorization', tokens['access_token'])])

        self.assertEqual(response.status_code, 403)

# authenticate
# send access token and possibly refresh token

# validating token in decode access token function

# logout and revoking access token and refresh token
# using rotating refresh token

# use redis to store refresh token families
# check for invalid refresh tokens