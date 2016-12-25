#!fl-mega/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import User

# a more complex setup could include several groups of tests each represented
# by a untittest.TestCase subclass, and each group then would have
# independent setUp an tearDown methods

class TestCase(unittest.TestCase):
    # run before each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    # run after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        """
            Makes sure that the Gravatar avatar URLs from the
            previous article are generated correctly
        """
        u = User(nickname='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_make_unique_nickname(self):
        """
            Verifies the make_unique_nickname method in the User classls
        """
        u = User(nickname='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        nickname = User.make_unique_nickname('john')
        assert nickname != 'john'
        u = User(nickname=nickname, email='susan@example.com')
        db.session.add(u)
        db.session.commit()
        nickname2 = User.make_unique_nickname('john')
        assert nickname2 != 'john'
        assert nickname2 != nickname

if __name__ == '__main__':
    unittest.main()
