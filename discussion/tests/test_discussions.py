import json
import unittest
from discussion.models.user import User
from discussion.app import create_app, db
from discussion.fixtures import discussion_fixture, user_fixture
from flask import url_for


class DiscussionViewsTest(unittest.TestCase):

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
        self.dana_token = 'token ' + self.client.post(url_for('users.login_user'), json=user_fixture['user_dana_valid']).json['token']
        
    
    def tearDown(self):
        db.drop_all()
        self.reqctx.pop()
        self.appctx.pop()
    
    def test_create_discussion(self):
        response = self.client.post(url_for('discussions.create_discussions', ),
                json=discussion_fixture['dana_first_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(User.query.get(1).created_discussions), 1)
    
    def test_edit_discussion(self):
        self.client.post(url_for('discussions.create_discussions', ),
                json=discussion_fixture['dana_first_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
        response = self.client.put(url_for('discussions.edit_discussion_detail', discussion_id='1'),
                json=discussion_fixture['dana_second_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 200)
    
    def test_create_invalid_discussion(self):
        response = self.client.post(url_for('discussions.create_discussions'),
                json=discussion_fixture['dana_first_discussion_invalid'],
                headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 400)
    
    def test_create_repetative_discussion(self):
        self.client.post(url_for('discussions.create_discussions'),
                json=discussion_fixture['dana_first_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
        response = self.client.post(url_for('discussions.create_discussions'),
                json=discussion_fixture['dana_first_discussion_valid'],
                headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 400)