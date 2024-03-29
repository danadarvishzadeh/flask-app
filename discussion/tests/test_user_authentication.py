import unittest
from urllib import response
from discussion.app import create_app
from discussion.extentions import db, redis
from discussion.tests.fixtures import user_fixture, discussion_fixture
from flask import url_for


class TestUserAuthentication(unittest.TestCase):

    def setUp(self):
        app = create_app(config_name='testing')
        self.client = app.test_client()
        self.appctx = app.app_context()
        self.appctx.push()
        self.reqctx = app.test_request_context()
        self.reqctx.push()
        db.drop_all()
        db.create_all()
        self.client.post(url_for('users.UserView'), json=user_fixture['dana_valid'])
        self.client.post(url_for('users.UserView'), json=user_fixture['mamad_valid'])
        
    def tearDown(self):
        db.session.close()
        db.drop_all()
        redis.connection.flushdb()
        self.appctx.pop()
        self.reqctx.pop()

    def test_authentication_endpoint(self):
        response = self.client.post(url_for('users.LoginView'),
                            json={
                                'username': user_fixture['dana_valid']['username'],
                                'password': user_fixture['dana_valid']['password'],
                            },
                            headers=[('User-Agent', 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36')])
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)
    
    def test_refresh_token(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    },
                                    headers=[('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0')]).json
        response = self.client.put(url_for('users.SessionView'),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}"),
                                    ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0')],
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
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])
        response = self.client.get(url_for('invites.InvitationView', discussion_id=1),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])
        
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url_for('invites.InvitationView', discussion_id=1),
                                    headers=[('Authorization', f"Bearer wrong token")])
        self.assertEqual(response.status_code, 401)
    
        response = self.client.get(url_for('invites.InvitationView', discussion_id=1),
                                    headers=[('Authorization', f"Bearer")])
        self.assertEqual(response.status_code, 401)
    
    def test_using_old_refresh_token(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json
        self.client.post(url_for('discussions.DiscussionView'),
                                    json=discussion_fixture['dana_first_discussion_valid'],
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])
        
        new_tokens = self.client.put(url_for('users.SessionView'),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")],
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    }).json
        response = self.client.put(url_for('users.SessionView'),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")],
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    })
        self.assertEqual(response.status_code, 401)

        response = self.client.get(url_for('invites.InvitationView', discussion_id=1),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])

        self.assertEqual(response.status_code, 401)
    
    def test_revoke_access_token(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json

        self.client.get(url_for('users.LogoutView'),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])
        
        response = self.client.put(url_for('users.SessionView'),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")],
                                    json={
                                        'refresh_token': tokens['refresh_token'],
                                    })
        self.assertEqual(response.status_code, 401)

        response = self.client.get(url_for('invites.InvitationView', discussion_id=1),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])

        self.assertEqual(response.status_code, 401)

    def test_get_all_sessions(self):
        tokens = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    }).json
        response = self.client.get(url_for('users.SessionView'),
                                    headers=[('Authorization', f"Bearer {tokens['access_token']}")])
        print(response.json)
        self.assertEqual(response.status_code, 200)

    def test_session_limit_exceeded(self):
        self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    },
                                    headers=[('User-Agent', 'a')])
        response = self.client.post(url_for('users.LoginView'),
                                    json={
                                        'username': user_fixture['dana_valid']['username'],
                                        'password': user_fixture['dana_valid']['password'],
                                    },
                                    headers=[('User-Agent', 'b')])
        self.assertEqual(response.status_code, 400)

    # def test_reset_password(self):
    #     tokens = self.client.post(url_for('users.LoginView'),
    #                                 json={
    #                                     'username': user_fixture['dana_valid']['username'],
    #                                     'password': user_fixture['dana_valid']['password'],
    #                                 }).json
    #     response = self.client.get(url_for('users.ResetPasswordView'),
    #                                 headers=[('Authorization', f"Bearer {tokens['access_token']}")])
    #     self.assertEqual(response.status_code, 200)


# authenticate
# send access token and possibly refresh token

# validating token in decode access token function

# logout and revoking access token and refresh token
# using rotating refresh token

# use redis to store refresh token families
# check for invalid refresh tokens