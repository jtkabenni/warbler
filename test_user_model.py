"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        u1 = User.signup(
            "testuser1","test@test.com", "password", None
        )
        u2 = User.signup(
            "testuser2","test2@test.com", "password2", None
        )
        db.session.add(u1, u2)
        db.session.commit()
        self.u1=u1
        self.u2=u2
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""
        u = User(
            email="tes3t@test.com",
            username="testuser3",
            password="password"
        )
        db.session.add(u)
        db.session.commit()
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_follows(self):
        """Does is_following successfully detect when user2 is following user1?
        Does is_following successfully detect when user1 is not following user2?"""
        follow=Follows(user_being_followed_id=self.u1.id, user_following_id=self.u2.id)
        db.session.add(follow)
        db.session.commit()
        self.assertTrue(User.is_following(self.u2, self.u1))
        self.assertFalse(User.is_following(self.u1, self.u2))


    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?
        Does is_followed_by successfully detect when user2 is not followed by user1?"""
        follow=Follows(user_being_followed_id=self.u1.id, user_following_id=self.u2.id)
        db.session.add(follow)
        db.session.commit()
        self.assertTrue(User.is_followed_by(self.u1, self.u2))
        self.assertFalse(User.is_followed_by(self.u2, self.u1))

    def test_successful_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""
        user = User.signup("testsignup", "test@signup.com", "testpassword", None)
        db.session.add(user)
        db.session.commit()
        self.assertEqual(len(User.query.all()), 3)
        self.assertEqual(user.username, "testsignup")

    def test_invalid_signup_duplicate_username(self):
        """Does User.signup fail to create a new user if username is a duplicate?"""
        user = User.signup("testuser1", "test@signup.com", "testpassword", None)
        db.session.add(user)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_signup_missing_username(self):
        """Does User.signup fail to create a new user if username is missing?"""
        user = User.signup(None, "test@signup.com", "testpassword", None)
        db.session.add(user)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authenticate_user(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        user = User.authenticate("testuser1", "password")
        self.assertEqual(user, self.u1)

    def test_invalid_username_authenticate_user(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        user = User.authenticate("testuser5", "password")
        self.assertEqual(user, False)

    def test_invalid_password_authenticate_user(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        user = User.authenticate("testuser1", "passworddd")
        self.assertEqual(user, False)

