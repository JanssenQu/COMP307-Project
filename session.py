from datetime import datetime, timedelta
from database import *
import secrets

EXPIRY_TIME = timedelta(minutes = 10)
TIMEOUT = timedelta(minutes = 30)

def generate_key():
    return secrets.token_urlsafe(16)

def create_session(user_id):
    session_key = generate_key()
    now = datetime.now()
    mutate_db('DELETE FROM sessions WHERE user_id = ?', [user_id])
    mutate_db('INSERT INTO sessions VALUES (?, ?, ?, ?)', [session_key, user_id, now + EXPIRY_TIME, now])
    return session_key

def verify_session(session_id):
    expiry_string = query_db('SELECT expiry_date FROM sessions WHERE session_id = ?', [session_id], True)
    if expiry_string is None:
        return None
    now = datetime.now()
    expiry_date = datetime.strptime(expiry_string['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
    if now > expiry_date:
        old_session = query_db('SELECT user_id, last_activity FROM sessions WHERE session_id = ?', [session_id], True)
        last_activity = datetime.strptime(old_session['last_activity'], '%Y-%m-%d %H:%M:%S.%f')
        mutate_db('DELETE FROM sessions WHERE session_id = ?', [session_id])
        if (now > last_activity + TIMEOUT):
            return None
        else:
            session_key = create_session(old_session['user_id'])
            return session_key
    else:
        mutate_db('UPDATE sessions SET last_activity = ? WHERE session_id = ?', [now, session_id])
        return session_id
