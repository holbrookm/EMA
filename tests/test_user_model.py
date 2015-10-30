import unittest2
from app.models import User, Role, db
from flask.ext.sqlalchemy import SQLAlchemy

class UserModeltestCase(unittest2.TestCase):
    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)
        
    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password
            
    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('Dog'))
        
    def test_password_salts_are_random(self):
        u = User (password = 'cat')
        u2 = User(password = 'dog')
        self.assertTrue (u.password_hash != u2.password_hash)
        
    def test_db_exists(self):
        self.assertTrue(db is not None)
        
    def test_table_role_exists(self):
        self.assertTrue(Role is not None)
    
    def test_table_user_exists(self):
        self.assertTrue(User is not None)
        
    def test_users_exist(self):
        self.assertTrue(User.query.all() is not None)
    
    def test_roles_exist(self):
        self.assertTrue(Role.query.all() is not None)
        
        