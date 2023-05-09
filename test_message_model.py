import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
db.create_all()

class UserMessageTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        u1 = User.signup(
            "testuser1","test@test.com", "password", None
        )
        u2 = User.signup(
            "testuser2","test2@test.com", "password2", None
        )
        db.session.add(u1, u2)
        db.session.commit()

        m1 = Message(text="Test message number 1.", user_id=u1.id)

        m2 = Message(text="Test message number 2.", user_id=u1.id)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.u1=u1
        self.u2=u2
        self.m1=m1
        self.m2=m2

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        self.assertEqual(len(Message.query.all()), 2)

    def test_user_messages(self):
        """Verify added messages are associated with user"""
        user = User.query.get_or_404(self.u1.id)
        self.assertEqual(len(user.messages), 2)

    def test_message_content(self):
        """Verify added message has correct text"""
        message = Message.query.get_or_404(self.m1.id)
        self.assertEqual(message.text, "Test message number 1.")

    def test_liked_messages(self):
        """Verify liked messages are successfully detected."""
        likes=[Likes(user_id=self.u2.id, message_id=self.m1.id), Likes(user_id=self.u2.id, message_id=self.m2.id)]
        db.session.add_all(likes)
        db.session.commit()
        self.assertEqual(len(self.u2.likes), 2)

  