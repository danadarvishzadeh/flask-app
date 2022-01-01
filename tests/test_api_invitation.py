import json
import unittest

from discussion.app import create_app, db
from discussion.fixtures import *
from flask import url_for
from discussion.models import User


class InvitationViewsTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.reqctx = self.app.test_request_context()
        self.reqctx.push()
        db.drop_all()
        db.create_all()
        self.client.post(url_for('api.create_users'), json=user_fixture['user_dana_valid'])
        self.client.post(url_for('api.create_users'), json=user_fixture['user_mamad_valid'])
        self.dana_token = 'token ' + self.client.post(url_for('auth.login_user'), json=user_fixture['user_dana_valid']).json['token']
        self.mamad_token = 'token ' + self.client.post(url_for('auth.login_user'), json=user_fixture['user_mamad_valid']).json['token']
        response = self.client.post(url_for('api.create_discussions', ),
                json=discussion_fixture['dana_first_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
    
    def tearDown(self):
        db.drop_all()
        self.reqctx.pop()
        self.appctx.pop()
    
    def test_send_invitation(self):
        response = self.client.post(url_for('api.create_invitations', discussion_id=1, user_id=2),
                                json=invitation_fixture['invite'],
                                headers=[('Authorization', self.dana_token),])  
        self.assertEqual(response.status_code, 200)
    
    def test_send_repeatative_invitations(self):
        self.client.post(url_for('api.create_invitations', discussion_id=1, user_id=2),
                                json=invitation_fixture['invite'],
                                headers=[('Authorization', self.dana_token),])  
        response = self.client.post(url_for('api.create_invitations', discussion_id=1, user_id=2),
                                json=invitation_fixture['invite'],
                                headers=[('Authorization', self.dana_token),])  
        self.assertEqual(response.status_code, 400)
    
    def test_accept_invitation(self):
        self.client.post(url_for('api.create_invitations', discussion_id=1, user_id=2),
                                json=invitation_fixture['invite'],
                                headers=[('Authorization', self.dana_token),])  
        response = self.client.put(url_for('api.edit_invitation_details', id=1),
                                json={'status': 'Accepted'},
                                headers=[('Authorization', self.mamad_token),])
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(User.query.get(1).host_for[0].host, User)
    
    def test_delete_invitation(self):
        self.client.post(url_for('api.create_invitations', discussion_id=1, user_id=2),
                                json=invitation_fixture['invite'],
                                headers=[('Authorization', self.dana_token),])
        response = self.client.delete(url_for('api.edit_invitation_details', id=1),
                                headers=[('Authorization', self.mamad_token),])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(User.query.get(1).invitations_sent), 0)