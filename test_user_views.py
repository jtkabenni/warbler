"""User route tests."""


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

from app import app, CURR_USER_KEY

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
        db.session.commit()
        self.u1=u1
        self.u2=u2
        self.client = app.test_client()

    def setup_followers(self):
        follow=Follows(user_being_followed_id=self.u1.id, user_following_id=self.u2.id)
        db.session.add(follow)
        db.session.commit()

    def test_index_unauthenticated(self):
        """View sign up and login when unauthenticated"""
        response = self.client.get('/') 
        self.assertIn(b"Sign up",response.data )
        self.assertIn(b"Log in",response.data )
        self.assertNotIn(b"Log out",response.data )
    
    def test_users_unauthenticated(self):
        """View users list as unauthenticated user"""
        response = self.client.get('/users')
        self.assertIn(b"testuser1", response.data)
    
    def test_user_following_unauthenticated(self):
        """Returns unauthorized when viewing user's following page as unauthorized user"""
        response = self.client.get(f'users/{self.u1.id}/following',follow_redirects=True)
        self.assertIn(b"Access unauthorized", response.data)
    
    def test_user_followers_unauthenticated(self):
        """Returns unauthorized when viewing user's followers page as unauthorized user"""
        response = self.client.get(f'users/{self.u1.id}/followers',follow_redirects=True)
        self.assertIn(b"Access unauthorized", response.data)
  
    def test_user_following(self):
        """Show user's following page as authorized user"""
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                user2 = User.query.get(self.u2.id)
            response = c.get(f'users/{user2.id}/following')
            self.assertIn(b"@testuser1", response.data)

    def test_user_followers(self):
        """Show user's followers page as authorized user"""
        self.setup_followers()

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            response = c.get(f'users/{self.u1.id}/followers')
            self.assertIn(b"@testuser2", response.data)
