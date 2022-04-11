from datetime import datetime, timedelta
from database import *
import secrets
import enum

EXPIRY_TIME = timedelta(minutes = 10)
TIMEOUT = timedelta(minutes = 30)

class User(enum.Enum):
    admin = "admins"
    sys_op = "sys_ops"
    student = "students"
    ta = "tas"
    prof = "profs"

def generate_key():
    return secrets.token_urlsafe(16)

def create_session(user_id):
    session_key = generate_key()
    now = datetime.now()
    mutate_db('DELETE FROM sessions WHERE user_id = ?', [user_id])
    mutate_db('INSERT INTO sessions VALUES (?, ?, ?, ?)', [session_key, user_id, now + EXPIRY_TIME, now])
    return session_key

def delete_session(session_id):
    mutate_db('DELETE FROM sessions WHERE session_id = ?', [session_id])

def verify_session(session_id):
    expiry_string = query_db('SELECT expiry_date FROM sessions WHERE session_id = ?', [session_id], True)
    if expiry_string is None:
        return None
    now = datetime.now()
    expiry_date = datetime.strptime(expiry_string['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
    if now > expiry_date:
        old_session = query_db('SELECT user_id, last_activity FROM sessions WHERE session_id = ?', [session_id], True)
        last_activity = datetime.strptime(old_session['last_activity'], '%Y-%m-%d %H:%M:%S.%f')
        delete_session(session_id)
        if (now > last_activity + TIMEOUT):
            return None
        else:
            session_key = create_session(old_session['user_id'])
            return session_key
    else:
        mutate_db('UPDATE sessions SET last_activity = ? WHERE session_id = ?', [now, session_id])
        return session_id


def get_user_id(session_id):
    query = query_db(f"Select user_id FROM sessions WHERE session_id = '{session_id}' ")
    user_id = None
    for value in query:
        user_id = dict(value).get("user_id")
    return user_id


def has_access_to_orange(session_id):
    return check_group(User.admin,session_id) or check_group(User.sys_op,session_id)


def has_access_to_blue(session_id):
    return check_group(User.prof,session_id) or check_group(User.admin,session_id) or check_group(User.ta,session_id) or check_group(User.sys_op,session_id)


def check_group(user_group,session_id):
    '''
    Verify if the user with the session id is in user_group
    :param user_group: User enum
    :param session_id: session_id of the user
    :return: True if the user is part of the group
    '''

    user_id = get_user_id(session_id)
    if user_id is None:
        return False

    query = query_db(f"Select user_id FROM {user_group.value} WHERE user_id = {user_id} ")
    in_group = None
    for value in query:
        in_group = dict(value).get("user_id")

    return in_group is not None
