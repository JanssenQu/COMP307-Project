import hashlib
from database import *

def hash_password(password):
    h = hashlib.md5(password.encode())
    return h.hexdigest()

def verify_user(username, password):
    hashed_pass = hash_password(password)
    user = query_db('SELECT user_id FROM users WHERE username = ? AND password = ? AND active = 1', [username, hashed_pass], True)
    return user