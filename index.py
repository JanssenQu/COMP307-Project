from flask import Flask, redirect, url_for, render_template, request
from database import *

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("page", name="login"))

@app.route("/<name>/")
def page(name):
    return render_template(name + ".html")

@app.route("/register/", methods=['POST','GET'])
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

        return redirect(url_for("page", name="login"))

    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run()