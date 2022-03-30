from unicodedata import name
from flask import Flask, redirect, url_for, render_template, request
from database import *

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login/", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        usr = request.form['usrname']
        pwd = request.form['psw']  # todo encrypt the password
        id = query_db('SELECT user_id FROM users WHERE username = ? AND password = ?', [usr, pwd])
        if id:
            #create session entry and pass it to dashboard
            return redirect(url_for("dashboard", session_id=1234))
        else:
            msg = 'Wrong username or password.'
            return render_template('login.html', msg = msg)
    
    return render_template("login.html")

@app.route("/register/", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # get form items
        uid = int(request.form['uid'])
        fname = request.form['fname']
        lname = request.form['lname']
        email =request.form['email']
        usr = request.form['usrname']
        pwd = request.form['psw']  # todo encrypt the password
        # checkboxes
        student = request.form.getlist('student') # empty list if not checked "Student" if checked
        ta = request.form.getlist('ta')
        prof = request.form.getlist('prof')
        admin = request.form.getlist('admin')
        sysop = request.form.getlist('sysop')

        # save to db
        mutate_db('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  [uid, fname, lname, email, usr, pwd, None, None, None])

        if student and not ta:
            mutate_db('INSERT INTO students VALUES (?, ?, ?, ?)',
                      [uid, None, None, None])
        if ta: # in case just checked ta and not student
            mutate_db('INSERT INTO students VALUES (?, ?, ?, ?)',
                      [uid, None, None, None])
            mutate_db('INSERT INTO tas VALUES (?)',[uid])

        if prof:
            mutate_db('INSERT INTO profs VALUES (?)',[uid])

        if admin:
            mutate_db('INSERT INTO admins VALUES (?)', [uid])

        if sysop:
            mutate_db('INSERT INTO sys_ops VALUES (?)', [uid])

        return redirect(url_for("login"))

    return render_template('register.html')

@app.route("/dashboard/<session_id>", methods=['GET', 'POST'])
def dashboard(session_id):
    #use the session id to gather all information about the user to display it on dashboard
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run()