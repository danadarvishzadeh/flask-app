import json
import unittest

from discussion.app import create_app, db
from discussion.tests.fixtures import *
from flask import url_for
from discussion.models.user import User


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
        self.client.post(url_for('users.create_users'), json=user_fixture['user_dana_valid'])
        self.client.post(url_for('users.create_users'), json=user_fixture['user_mamad_valid'])
        self.dana_token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        self.mamad_token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_mamad_valid']).json['token']
        response = self.client.post(url_for('discussions.create_discussions', ),
                json=discussion_fixture['dana_first_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
    
    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.reqctx.pop()
        self.appctx.pop()
    
    def test_create_follows_valid(self):
        response = self.client.post(url_for('follow.create_follows', discussion_id=1),
                        headers=[('Authorization', self.mamad_token),])
        self.assertEqual(response.status_code, 200)
    
    def test_create_follows_invalid(self):
        response = self.client.post(url_for('follow.create_follows', discussion_id=1),
                        headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 403)
    
    def test_delete_follow(self):
        self.client.post(url_for('follow.create_follows', discussion_id=1),
                        headers=[('Authorization', self.mamad_token),])
        response = self.client.delete(url_for('follow.delete_follows', discussion_id=1),
                        headers=[('Authorization', self.mamad_token),])
        self.assertEqual(response.status_code, 200)
    
    def test_create_follow_repeatative(self):
        self.client.post(url_for('follow.create_follows', discussion_id=1),
                        headers=[('Authorization', self.mamad_token),])
        response = self.client.post(url_for('follow.create_follows', discussion_id=1),
                        headers=[('Authorization', self.mamad_token),])
        self.assertEqual(response.status_code, 400)