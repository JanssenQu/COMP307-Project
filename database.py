import sqlite3

DATABASE = 'database.sqlite'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    with open('schema.sql') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

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

def main():
    # example on how to use the database functions
    #init_db()
    #mutate_db('INSERT INTO USERS VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [1, 'john', 'doe', 'example@mail.com', 'joe', 'abcd', None, None, None])
    users = query_db('SELECT * FROM USERS')
    for value in users:
        print(dict(value))

if __name__ == '__main__':
    main()