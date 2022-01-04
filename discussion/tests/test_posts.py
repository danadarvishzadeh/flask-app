import json
import unittest

from discussion.app import create_app, db
from discussion.fixtures import *
from flask import url_for


class PostViewsTest(unittest.TestCase):

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
        db.drop_all()
        self.reqctx.pop()
        self.appctx.pop()
    
    def test_post_creation(self):
        response = self.client.post(url_for('posts.create_posts', discussion_id=1),
                        json=post_fixture['discussion1_post1'],
                        headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 200)
    
    def test_get_posts(self):
        self.client.post(url_for('posts.create_posts', discussion_id=1),
        json=post_fixture['discussion1_post1'],
                headers=[('Authorization', self.dana_token),])
        response = self.client.get(url_for('posts.get_posts'))
        self.assertEqual(response.status_code, 200)
    
    def test_get_post_detail(self):
        self.client.post(url_for('posts.create_posts', discussion_id=1),
        json=post_fixture['discussion1_post1'],
                headers=[('Authorization', self.dana_token),])
        response = self.client.get(url_for('posts.get_post_detail', post_id=2))
        self.assertEqual(response.status_code, 400)
    
    def test_edit_post_details(self):
        self.client.post(url_for('posts.create_posts', discussion_id=1),
        json=post_fixture['discussion1_post1'],
                headers=[('Authorization', self.dana_token),])
        response = self.client.put(url_for('posts.edit_post_details', post_id=1),
                json=post_fixture['discussion1_post2'],
                headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 200)
    
    def test_edit_post_details_without_permission(self):
        self.client.post(url_for('posts.create_posts', discussion_id=1),
                json=post_fixture['discussion1_post1'],
                headers=[('Authorization', self.dana_token),])
        response = self.client.put(url_for('posts.edit_post_details', post_id=1),
                json=post_fixture['discussion1_post2'],
                headers=[('Authorization', self.mamad_token),])
        self.assertEqual(response.status_code, 403)