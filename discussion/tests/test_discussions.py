import json
import unittest
from discussion.models.user import User
from discussion.app import create_app, db
from discussion.tests.fixtures import discussion_fixture, user_fixture, post_fixture
from flask import url_for
from discussion.models.discussion import Discussion


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
        self.client.post(url_for('users.UserView'),
                        json=user_fixture['dana_valid'])
        self.dana_token = 'Bearer ' + self.client.post(
            url_for('users.LoginView'), json=user_fixture['dana_valid']).json['access_token']

    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.reqctx.pop()
        self.appctx.pop()

    def test_create_discussion(self):
        response = self.client.post(url_for('discussions.DiscussionView', ),
                                    json=discussion_fixture['dana_first_discussion_valid'],
                                    headers=[('Authorization', self.dana_token),])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(User.query.get(1).owned_discussions), 1)

    def test_edit_discussion(self):
        self.client.post(url_for('discussions.DiscussionView', ),
                         json=discussion_fixture['dana_first_discussion_valid'],
                         headers=[('Authorization', self.dana_token), ])
        response = self.client.put(url_for('discussions.DiscussionDetailView', discussion_id='1'),
                                   json=discussion_fixture['dana_second_discussion_valid'],
                                   headers=[('Authorization', self.dana_token), ])
        self.assertEqual(response.status_code, 204)

    def test_create_invalid_discussion(self):
        response = self.client.post(url_for('discussions.DiscussionView'),
                                    json=discussion_fixture['dana_first_discussion_invalid'],
                                    headers=[('Authorization', self.dana_token), ])
        self.assertEqual(response.status_code, 422)

    def test_create_repetative_discussion(self):
        self.client.post(url_for('discussions.DiscussionView'),
                        json=discussion_fixture['dana_first_discussion_valid'],
                        headers=[('Authorization', self.dana_token), ])
        response = self.client.post(url_for('discussions.DiscussionView'),
                                    json=discussion_fixture['dana_first_discussion_valid'],
                                    headers=[('Authorization', self.dana_token), ])
        self.assertEqual(response.status_code, 400)

    # def test_discussion_paginator(self):
    #     self.client.post(url_for('discussions.DiscussionView'),
    #                     json=discussion_fixture['dana_first_discussion_valid'],
    #                     headers=[('Authorization', self.dana_token), ])
    #     self.client.post(url_for('discussions.DiscussionView'),
    #                     json=discussion_fixture['dana_second_discussion_valid'],
    #                     headers=[('Authorization', self.dana_token), ])
    #     response = self.client.get(url_for('discussions.DiscussionDetailView'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('discussions', response.json)

    def test_get_existing_single_discussion(self):
        self.client.post(url_for('discussions.DiscussionView'),
                        json=discussion_fixture['dana_first_discussion_valid'],
                        headers=[('Authorization', self.dana_token), ])
        response = self.client.get(
            url_for('discussions.DiscussionDetailView', discussion_id=1))
        self.assertEqual(response.status_code, 200)

    def test_get_non_existing_single_discussion(self):
        response = self.client.get(
            url_for('discussions.DiscussionDetailView', discussion_id=1))
        self.assertEqual(response.status_code, 404)

    def test_edit_discussion_with_invalid_data(self):
        self.client.post(url_for('discussions.DiscussionView'),
                        json=discussion_fixture['dana_first_discussion_valid'],
                        headers=[('Authorization', self.dana_token), ])
        response = self.client.put(url_for('discussions.DiscussionDetailView', discussion_id=1), json=discussion_fixture['dana_first_discussion_invalid'], headers=[('Authorization', self.dana_token), ])
        self.assertEqual(response.status_code, 422)
    
    def test_delete_discussion(self):
        self.client.post(url_for('discussions.DiscussionView'),
                        json=discussion_fixture['dana_first_discussion_valid'],
                        headers=[('Authorization', self.dana_token), ])
        response = self.client.delete(url_for('discussions.DiscussionDetailView', discussion_id=1), headers=[('Authorization', self.dana_token), ])
        self.assertEqual(response.status_code, 204)
        discussion = Discussion.query.get(1)
        self.assertEqual(discussion, None)