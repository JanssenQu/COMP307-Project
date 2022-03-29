import sqlite3
from flask import _app_ctx_stack

DATABASE = 'database.db'

def init_db():
    db = get_db()
    with open('schema.sql') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(DATABASE)
    return top.sqlite_db

@app.teardown_appcontext
def close_connection(exception):
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def mutate_db(mutation, args=()):
    db = get_db()
    cur = db.execute(mutation, args)
    db.commit()
    cur.close()