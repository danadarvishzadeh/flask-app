# from discussion.blueprints.auth import *
# from discussion.blueprints.api import create_user
import unittest
from discussion.models import User
from discussion.app import create_app, db

user_fixture = {
    "user_dana_valid": {
        "username": "dana",
        "email": "dana@dana.com",
        "name": "dana",
        "lastname": "danaplastiki",
        "password": "123456789"
    },
    "user_mamad_valid": {
        "username": "mamad",
        "email": "mamad@dana.com",
        "name": "mamad",
        "lastname": "mamadplastiki",
        "password": "123456789"
    },
    "user_dana_rep": {
        "username": "dana",
        "email": "dana@dana.com",
        "name": "dana",
        "lastname": "danaplastiki",
        "password": "123456789"
    },
    "user_dana_invalid": {
        "username": 1,
        "email": "dana.dana.com",
        "name": "dana",
        "lastname": "danaplastiki",
        "password": "1234567"
    },
}


class UserAuthViewsTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing").test_client()
        self.db = db
        self.db.drop_all()
        self.db.create_all()
    
    def tearDown(self):
        self.db.drop_all()

    def test_create_user(self):
        response = self.app.post("/users/", data=users_fixture["user_dana_valid"])
        self.assertEqual(response.status_code, 200)
        self.assert_equal(response.json, {
    "name": "dana",
    "username": "dana",
    "invitations_sent": [],
    "email": "dana@dana.com",
    "id": 1,
    "lastname": "danaplastiki",
    "created_discussions": [],
    "invitations_recived": [],
    "followed_discussions": [],
    "host_for": [],
    "participated_discussions": [],
    "participated_with_users": []
})