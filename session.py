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


def has_access_to_orange(session_id):
    return is_admin(session_id) or is_sysop(session_id)


def has_access_to_blue(session_id):
    return is_prof(session_id) or is_admin(session_id) or is_ta(session_id) or is_sysop(session_id)


def is_prof(session_id):
    query = query_db(f"Select user_id FROM sessions WHERE session_id = '{session_id}' ")
    user_id = None
    for value in query:
        user_id = dict(value).get("user_id")

    if user_id is None:
        return False

    query = query_db(f"Select user_id FROM profs WHERE user_id = {user_id} ")
    is_prof = None
    for value in query:
        is_prof = dict(value).get("user_id")

    return is_prof is not None



def is_sysop(session_id):
    query = query_db(f"Select user_id FROM sessions WHERE session_id = '{session_id}' ")
    user_id = None
    for value in query:
        user_id = dict(value).get("user_id")

    if user_id is None:
        return False

    query = query_db(f"Select user_id FROM sys_ops WHERE user_id = {user_id} ")
    is_sysop = None
    for value in query:
        is_sysop = dict(value).get("user_id")

    return is_sysop is not None


def is_ta(session_id):
    query = query_db(f"Select user_id FROM sessions WHERE session_id = '{session_id}' ")
    user_id = None
    for value in query:
        user_id = dict(value).get("user_id")

    if user_id is None:
        return False

    query = query_db(f"Select user_id FROM tas WHERE user_id = {user_id} ")
    is_ta = None
    for value in query:
        is_ta = dict(value).get("user_id")

    return is_ta is not None


def is_admin(session_id):
    query = query_db(f"Select user_id FROM sessions WHERE session_id = '{session_id}' ")
    user_id = None
    for value in query:
        user_id = dict(value).get("user_id")

    if user_id is None:
        return False

    query = query_db(f"Select user_id FROM admins WHERE user_id = {user_id} ")
    is_admin = None
    for value in query:
        is_admin = dict(value).get("user_id")

    return is_admin is not None