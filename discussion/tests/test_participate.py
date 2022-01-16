import json
import unittest
from discussion.utils.errors import JsonPermissionDenied, ResourceDoesNotExists
from discussion.app import create_app, db
from discussion.tests.fixtures import *
from flask import url_for
from discussion.models.user import User



# class PermissionToAddPostTest(unittest.TestCase):

#     def setUp(self):
#         self.app = create_app('testing')
#         self.client = self.app.test_client()
#         self.appctx = self.app.app_context()
#         self.appctx.push()
#         self.reqctx = self.app.test_request_context()
#         self.reqctx.push()
#         db.drop_all()
#         db.create_all()
#         self.client.post(url_for('api.create_users'), json=user_fixture['dana_valid'])
#         self.client.post(url_for('api.create_users'), json=user_fixture['mamad_valid'])
#         self.dana_token = 'token ' + self.client.post(url_for('auth.login_user'), json=user_fixture['dana_valid']).json['token']
#         self.mamad_token = 'token ' + self.client.post(url_for('auth.login_user'), json=user_fixture['mamad_valid']).json['token']
#         self.client.post(url_for('api.create_discussions', ),
#                             json=discussion_fixture['dana_first_discussion_valid'],
#                             headers=[('Authorization', self.dana_token),])
#         self.client.post(url_for('api.create_invitations', discussion_id=1, user_id=2),
#                             json=invitation_fixture['invite'],
#                             headers=[('Authorization', self.dana_token),])  
#         @premission_to_add_posts
#         def dummy_func(id):
#             return 1
#         self.decorated = dummy_func
    
#     def tearDown(self):
#         db.drop_all()
#         self.reqctx.pop()
#         self.appctx.pop()

#     def test_creator_permission_to_add_posts_decorator(self):
#         self.assertEqual(self.decorated(id=1), 1)

#     def test_user_dont_have_permission_to_add_posts_decorator(self):
#         self.appctx.g.user = User.query.get(2)
#         with self.assertRaises(JsonPermissionDenied):
#             self.decorated(id=1)
        
#     def test_participant_permission_add_post_to_discussion(self):
#         self.client.put(url_for('api.edit_invitation_details', invitation_id=1),
#                             json={'status': 'Accepted'},
#                             headers=[('Authorization', self.mamad_token),])
#         self.assertEqual(self.decorated(id=1), 1)
    
#     def test_no_discussion_participant_permission_add_post_to_discussion(self):
#         with self.assertRaises(ResourceDoesNotExists):
#             self.decorated(id=2)