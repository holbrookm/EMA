import unittest2
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        #db.create_all()  #When this is active, the DB is wiped

    def tearDown(self):
        db.session.remove()
        #db.drop_all() #When this is active, the DB is wiped
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['DEBUG'])

